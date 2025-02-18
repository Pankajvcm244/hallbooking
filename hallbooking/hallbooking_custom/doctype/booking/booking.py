# Copyright (c) 2025, Pankaj Sharma and contributors
# For license information, please see license.txt


import frappe , json
from frappe.utils.password import get_decrypted_password
from frappe.model.document import Document
import requests
from frappe.utils import now_datetime
from datetime import timedelta, datetime
from frappe.utils import getdate, today, date_diff
from frappe.utils import add_days, add_months, now_datetime, get_datetime, format_datetime


# import logging
# logging.basicConfig(level=logging.DEBUG)
#add "log_level": "DEBUG" in site_config.json to enable debug logs
# logs will apppear in logs/web.error.log
#logging.debug("This is a debug message")
#logging.info("This is an info message")
#logging.error("This is an error message")

class booking(Document):
    
    def validate(self):
        self.validate_time_range()
        self.check_for_conflicts()

    def before_save(self):
        #logging.debug(f"Before Save-1 {self.docstatus} ")
        # Add default time as calendar wants datetime format
        self.starttime = f"{self.date}T{self.from_time}"
        self.endtime = f"{self.date}T{self.to_time}"
        #logging.debug(f"Before Save-2 {self.starttime} {self.endtime}")   
        self.track_status_change()
        #logging.debug(f"Before Save-2 {self.docstatus} ")
    
    def before_insert(self):
        """
        Set the default value of booking_status based on restricted_only_via_approval.
        """
        #logging.debug(f"before insert-1 {self.restricted_only_via_approval}, {self.booking_status}")
        if self.restricted_only_via_approval == "No":
            self.booking_status = "Approved"
        else:
            self.booking_status = "Pending"  
        #logging.debug(f"before insert-1 {self.restricted_only_via_approval}, {self.booking_status}")  

    def validate_time_range(self):
        hall_booking_settings = frappe.get_doc("HallBooking Settings")
        #logging.debug(f"validate time range  {self.date}, {self.from_time}, {self.to_time}.  {hall_booking_settings.max_booking_duration}")  
        # Check if the booking start date is beyond the maximum allowed duration
        current_date = getdate(today())  
        # Calculate the maximum allowed booking date
        max_booking_date = add_days(current_date, hall_booking_settings.max_booking_duration)
        if getdate(self.date) > max_booking_date:
            frappe.throw(f"Room bookings cannot be made beyond {hall_booking_settings.max_booking_duration} days from today. The maximum allowed date is {max_booking_date}.")
        #Ensure that End Time is after Start Time.
        if self.to_time <= self.from_time:
            frappe.throw("End Time must be after Start Time.")
        # Check if the start date and time are in the past
        if getdate(self.date) < current_date:
            frappe.throw("Booking cannot be made for a past date or time.")
        #logging.debug(f"in conflict check {today}, {current_date}, {max_booking_date}, {self.date}")
        
    def check_for_conflicts(self):
        # Ensure no overlapping bookings for the same room
        ## AND booking_status = 'Approved'
        
        conflicts = frappe.db.sql("""
            SELECT name
            FROM `tabbooking`
            WHERE hall_name = %(hall_name)s            
            AND date = %(date)s
            AND (
                (from_time <= %(to_time)s AND to_time >= %(from_time)s)
            )  
            AND name != %(name)s
            AND booking_status != 'Cancelled'        
        """, {
            "hall_name": self.hall_name,
            "date": self.date,
            "from_time": self.from_time,
            "to_time": self.to_time,
            "name": self.name or ""
        })
        if conflicts:
            # this is to ensure for devotee case we don't make it Approved
            self.booking_status == "Pending"
            frappe.throw(f"The hall '{self.hall_label}' is already booked for during this time.")

    def track_status_change(self):
        # Check if the status has changed or if the document is new
        IT_flag = False
        Facility_flag = False
        Fnb_flag = False
        if self.is_new() or self.get_db_value("booking_status") != self.booking_status:
            self.flags.status_changed = True
            # Fetch Hall Booking settings
            hall_booking_settings = frappe.get_doc("HallBooking Settings")
            # Check if email notifications are enabled
            if hall_booking_settings.enable_email == "Yes":
                # Send status change email
                #self.send_status_change_email()                
                #logging.debug(f"track_status_change send email")
                # Additional emails for specific status
                if self.booking_status in ["Approved", "Cancelled"]:
                    # Send emails to IT, Facility, and F&B teams based on requirements
                    if self.it_team_requirements:
                        #self.send_IT_email()
                        IT_flag = True
                    if self.facility_team_requirements:
                        #self.send_facility_email()
                        Facility_flag = True
                    if self.food_and_beverage_team_requirements:
                        #self.send_fnb_email()
                        Fnb_flag = True
                self.send_email_approval_new(IT_flag, Facility_flag, Fnb_flag)
            if hall_booking_settings.enable_whatsup == "Yes":
                # Send status change email
                send_whatsapp_message(self.submitter_name, self.submitter_mobile, self.hall_label, self.booking_status, self.name, self.date, self.from_time, self.to_time)
        else:
            self.flags.status_changed = False
    
            
    # def send_status_change_email(self):
    #     #logging.debug("send email, with status value=%d", self.flags.status_changed)
    #     # Prepare email details
    #     hall_booking_settings = frappe.get_doc("HallBooking Settings")
    #     subject = f"{self.hall_label} {self.name} status changed to {self.booking_status}"
    #     message = f"""
    #         Dear {self.submitter_name}, <br> <br>
    #         The status of your room booking {self.name} has been updated to: {self.booking_status}. <br> <br>
    #         Booking Details: <br>
    #         Booking for room '{self.hall_label}'. <br>
    #         Booked by Name: {self.submitter_name}  <br>
    #         Booked by Email: {self.submitter_email}  <br>
    #         Booked by Mobile: {self.submitter_mobile}  <br>
    #         Date: {self.date} <br>
    #         Start Time: {self.from_time} <br>
    #         End Time: {self.to_time} <br>
    #         Purpose: {self.purpose} <br>  <br>

    #         Additional Facility Requested: <br>
    #         IT Facilities requested: <br> >
    #         {self.it_team_requirements} <br> 
    #         Facilities requested:  <br> >
    #         {self.facility_team_requirements } <br> 
    #         Food and Beverage Facilities requested: <br>  >
    #         {self.food_and_beverage_team_requirements} <br> <br>

    #         Regards,  <br>
    #         VCM Room Booking Team
    #      """
    #     facilityemail = hall_booking_settings.hall_booking_approver_email
    #     # Send the email
    #     # List of email recipients
    #     recipients = [""]
    #     recipients.append(self.submitter_email)  # Add the submitter's email
    #     # Convert the list into a comma-separated string
    #     recipients_str = ", ".join(recipients)
    #     frappe.sendmail(
    #         recipients= recipients_str,
    #         subject=subject,
    #         message=message,
    #         cc=[facilityemail],  # Optional CC emails
    #     )

    
    # def send_IT_email(self):
    #     hall_booking_settings = frappe.get_doc("HallBooking Settings")
    #     #logging.debug(f"send IT email, with {hall_booking_settings.it_team_email}")
    #     if hall_booking_settings.it_team_email:             
    #         subject = f"{self.hall_label} {self.name} has requested IT facilities "
    #         message = f"""
    #             Hare Krishna IT Team, <br> <br>
    #             Room booking {self.name} for room '{self.hall_label}' has requested IT facilities for their booking, and current status is {self.booking_status}, please do the needful. <br> <br>
    #             Booking Details: <br>
    #             Booking for room '{self.hall_label}'. <br>
    #             Booked by Name: {self.submitter_name}  <br>
    #             Booked by Email: {self.submitter_email}  <br>
    #             Booked by Mobile: {self.submitter_mobile}  <br>
    #             Start Time: {self.from_time} <br>
    #             End Time: {self.to_time} <br> 
    #             Purpose: {self.purpose} <br>  <br>
    #             IT Facilities requested: <br> >
    #                 {self.it_team_requirements} <br> <br>

    #             Regards,  <br>
    #             VCM Room Booking Team
    #         """
    #         # Send the email
    #         # List of email recipients
    #         recipients = []
    #         recipients.append(hall_booking_settings.it_team_email)  
    #         #logging.debug(f"send IT-3 email, with  {recipients}")
    #         # Convert the list into a comma-separated string
    #         recipients_str = ", ".join(recipients)
    #         #logging.debug(f"send IT-4 email, with  {recipients_str}")
    #         frappe.sendmail(
    #             recipients= recipients_str,
    #             subject=subject,
    #             message=message
    #         )   

    # def send_facility_email(self):
    #     hall_booking_settings = frappe.get_doc("HallBooking Settings")
    #     #logging.debug(f"send IT email, with {hall_booking_settings.facility_team_email}")
    #     if hall_booking_settings.facility_team_email:   
    #         subject = f"{self.hall_label} {self.name} has requested addiitonal facilities "
    #         message = f"""
    #             Hare Krishna Facility Team, <br> <br>
    #             Room booking {self.name} for room '{self.hall_label}' has requested additional facilities for their booking, and current status is {self.booking_status}, please do the needful. <br> <br>
    #             Booking Details: <br>
    #             Booking for room '{self.hall_label}'. <br>
    #             Booked by Name: {self.submitter_name}  <br>
    #             Booked by Email: {self.submitter_email}  <br>
    #             Booked by Mobile: {self.submitter_mobile}  <br>
    #             Start Time: {self.from_time} <br>
    #             End Time: {self.to_time} <br> 
    #             Purpose: {self.purpose} <br>  <br>
    #             Facilities requested:  <br> >
    #             {self.facility_team_requirements } <br> <br>
    #             Regards,  <br>
    #             VCM Room Booking Team
    #         """
    #         # Send the email
    #         # List of email recipients
    #         recipients = []
    #         recipients.append(hall_booking_settings.facility_team_email)  # Add the submitter's email
    #         #logging.debug(f"send Facilt-3 email, with {hall_booking_settings.facility_team_email}, {recipients}")
    #         # Convert the list into a comma-separated string
    #         recipients_str = ", ".join(recipients)
    #         #logging.debug(f"send IT-3 email, with {hall_booking_settings.facility_team_email}, {recipients_str}")
    #         frappe.sendmail(
    #             recipients= recipients_str,
    #             subject=subject,
    #             message=message
    #         )        
    # def send_fnb_email(self):
    #     hall_booking_settings = frappe.get_doc("HallBooking Settings")
    #     #logging.debug("send Food and Beverage email, with status value=%d", self.flags.status_changed)
    #     if hall_booking_settings.fnb_team_email:  
    #         # Prepare email details
    #         subject = f"{self.hall_label} {self.name} has requested Food and Beverage facilities"
    #         message = f"""
    #             Hare Krishna Food and Beverage Team, <br> <br>
    #             Room booking {self.name} for room '{self.hall_label}' has requested Food and Beverage facilities for their booking, and current status is {self.booking_status}, please do the needful. <br> <br>
    #             Booking Details: <br>
    #             Booking for room '{self.hall_label}'. <br>
    #             Booked by Name: {self.submitter_name}  <br>
    #             Booked by Email: {self.submitter_email}  <br>
    #             Booked by Mobile: {self.submitter_mobile}  <br>
    #             Start Time: {self.from_time} <br>
    #             End Time: {self.to_time} <br> 
    #             Purpose: {self.purpose} <br> 

                
    #             Food and Beverage Facilities requested: <br>  >
    #             {self.food_and_beverage_team_requirements} <br> <br>
    #             Regards,  <br>
    #             VCM Room Booking Team
    #         """
    #         # Send the email
    #         recipients = []
    #         recipients.append(hall_booking_settings.fnb_team_email)  # Add the submitter's email
    #         #logging.debug(f"send Fnb-3 email, with {hall_booking_settings.fnb_team_email}, {recipients}")
    #         # Convert the list into a comma-separated string
    #         recipients_str = ", ".join(recipients)
    #         #logging.debug(f"send FnB-3 email, with {hall_booking_settings.fnb_team_email}, {recipients_str}")
    #         frappe.sendmail(
    #             recipients= recipients_str,
    #             subject=subject,
    #             message=message
    #         )

    def send_email_approval_new(doc,IT_flag, Facility_flag, Fnb_flag):
        #logging.debug(f"**in send_email_approval vcm item rew 1 {currency}, {allowed_options}")
        template_data = {
            "doc": doc,
        }   
        hall_booking_settings = frappe.get_doc("HallBooking Settings") 
        facilityemail = hall_booking_settings.hall_booking_approver_email
        # Send the email
        # List of email recipients
        email_recipients = []
        email_recipients.append(doc.submitter_email)  # Add the submitter's email
        if IT_flag:
            email_recipients.append(hall_booking_settings.it_team_email)
        if Facility_flag:
            email_recipients.append(hall_booking_settings.facility_team_email)
        if Fnb_flag:
            email_recipients.append(hall_booking_settings.fnb_team_email)
        
        # Remove any empty or None values from the recipients list
        email_recipients = list(filter(None, email_recipients))

        #logging.debug(f"**in send_email_approval_new  {email_recipients} ************* ")
        frappe.sendmail(
            recipients= email_recipients, # Pass the list directly
            subject=f"VCM Hall Booking: {doc.hall_label} request status",
            message=frappe.render_template(
                "hallbooking/hallbooking_custom/utilities/email_templates/hall_booking_email_template.html", template_data ),
            cc=[facilityemail] if isinstance(facilityemail, str) else facilityemail if facilityemail else []
        )
        #logging.debug(f"**in send_email_approval_new vcm item req3 {IT_flag},{Facility_flag},{Fnb_flag} ************* ")
        return   


@frappe.whitelist()
def approve_booking(booking_id):
    """
    Approves a booking by updating its status to 'Approved' and saving the changes.
    """
    try:
        
        # Fetch the booking document
        booking = frappe.get_doc("booking", booking_id)
        #logging.debug(f"approve_booking {booking_id}, {booking.booking_status}, {booking.docstatus}")
        # Check if the booking is in a state that can be approved
        if booking.booking_status != "Pending":
            frappe.throw("Only bookings with status 'Pending' can be approved.")

        # Handle cancellation based on docstatus

        booking.booking_status = "Approved"
        booking.save()
        #logging.info(f"Booking {booking_id} status updated to 'Approved' (draft document).")

        #logging.debug(f"approve_booking {booking_id}, {booking.booking_status}, {booking.docstatus}")
        return f"Booking {booking_id} has been approved."

    except Exception as e:
        #logging.error(f"Error approving booking {booking_id}: {str(e)}")
        frappe.throw(f"An error occurred while approving the booking: {str(e)}")
    
    

@frappe.whitelist()
def cancel_booking(booking_id):
    try:
        # Fetch the booking document
        booking = frappe.get_doc("booking", booking_id)
        #logging.debug(f"cancel_booking {booking_id}, {booking.booking_status}, {booking.docstatus}")
        
        # Check if the booking is in a cancellable state
        if booking.booking_status not in ["Pending", "Approved"]:
            frappe.throw("Only Pending or Approved bookings can be cancelled.")

        # Handle cancellation based on docstatus
        if booking.docstatus == 1:  # Submitted
            booking.cancel()  # Automatically sets docstatus to 2
            #logging.info(f"Booking {booking_id} has been successfully cancelled (submitted document).")
        else:
            booking.booking_status = "Cancelled"
            booking.save()
            #logging.info(f"Booking {booking_id} status updated to 'Cancelled' (draft document).")
        #logging.info(f"Booking {booking_id} has been successfully cancelled.")
    except Exception as e:
        #logging.error(f"Error cancelling booking {booking_id}: {str(e)}")
        frappe.throw(f"An error occurred while cancelling the booking: {str(e)}") 
     


@frappe.whitelist()
def create_recurring_conference_bookings(room_booking_id):
    """
    Create recurring conference room bookings with specific date and time.
    Includes conflict checking and notifications.

    Args:
    room_booking_id (str): The ID of the RoomBookingVCM record.

    Returns:
    str: Success message with the number of bookings created.
    """
    # Fetch the original room booking document
    room_booking = frappe.get_doc("RoomBookingVCM", room_booking_id)

    if not room_booking.recurring or not room_booking.recurrence_frequency:
        frappe.throw("This booking is not marked as recurring or missing recurrence frequency.")

    # Recurrence parameters
    frequency = room_booking.recurrence_frequency  # Daily, Weekly, Monthly
    recurrence_count = room_booking.recurrence_count or 1  # Default to 1 if not set
    start_datetime = get_datetime(room_booking.start_datetime)  # Original start date and time
    end_datetime = get_datetime(room_booking.end_datetime)  # Original end date and time

    created_bookings = []  # To track the names of created bookings
    conflicts = []  # To track conflicting bookings

    for i in range(recurrence_count):
        # Calculate new start and end datetime based on frequency
        if frequency == "Daily":
            next_start_datetime = add_days(start_datetime, i)
            next_end_datetime = add_days(end_datetime, i)
        elif frequency == "Weekly":
            #next_start_datetime = add_weeks(start_datetime, i)
            #next_end_datetime = add_weeks(end_datetime, i)
            next_start_datetime = start_datetime + timedelta(weeks=i)
            next_end_datetime = end_datetime + timedelta(weeks=i)
        elif frequency == "Monthly":
            next_start_datetime = add_months(start_datetime, i)
            next_end_datetime = add_months(end_datetime, i)
        else:
            frappe.throw("Invalid recurrence frequency. Use 'Daily', 'Weekly', or 'Monthly'.")

        # Check for conflicts
        conflict = frappe.db.exists("RoomBookingVCM", {
            "room_name": room_booking.room_name,
            "start_datetime": ("<=", next_end_datetime),
            "end_datetime": (">=", next_start_datetime),
            "name": ("!=", room_booking.name),  # Exclude the original booking
            "booking_status": "Confirmed"  # Only consider confirmed bookings
        })

        if conflict:
            conflicts.append({
                "start_datetime": next_start_datetime,
                "end_datetime": next_end_datetime,
                "conflict_with": conflict,
            })
            continue  # Skip creating this booking

        # Create a new booking document
        new_booking = frappe.get_doc({
            "doctype": "RoomBookingVCM",
            "room_name": room_booking.room_name,
            "start_datetime": format_datetime(next_start_datetime),
            "end_datetime": format_datetime(next_end_datetime),
            "senior_devotee_name": room_booking.senior_devotee_name,
            "senior_devotee_email": room_booking.senior_devotee_email,
            "booking_status": "Draft",
            "recurring_reference": room_booking.name,  # Link to original booking
        })
        new_booking.insert()
        created_bookings.append(new_booking.name)
    frappe.db.commit()

    # Prepare the response
    if conflicts:
        conflict_message = f"{len(conflicts)} conflicts detected:\n" + "\n".join([
            f"Conflict with booking {c['conflict_with']} (From {c['start_datetime']} to {c['end_datetime']})"
            for c in conflicts
        ])
    else:
        conflict_message = "No conflicts detected."

    success_message = f"Successfully created {len(created_bookings)} bookings."
    return f"{success_message}\n\n{conflict_message}"


@frappe.whitelist()
def send_whatsapp_message(name, mobile, hall_name, booking_status, booking_id,date, from_time, to_time):
    whatsupsettings = frappe.get_doc("Hallbooking WhatsAPP Settings")
    # Fetch the booking document
    #booking = frappe.get_doc("booking", booking_id)
    
    doctype = "Hallbooking WhatsAPP Settings"  # Example of a singleton DocType
    fieldname = "token" 
    decrypted_value = get_decrypted_password(doctype, doctype, fieldname)
    #logging.debug(f"whatsup {name},{mobile}, {hall_name}, {booking_status},  {booking_id}, {whatsupsettings.template}, {date}, {from_time}, {to_time} ")
    if isinstance(date, str):
        jsondate = date        
    else:
        jsondate = date.isoformat()  # Convert to ISO 8601 format

    if isinstance(from_time,str):
        # Split by ':' and take the first two parts
        jsonstarttime = ":".join(from_time.split(":")[:2])      
    else:        
        # Convert timedelta to hours and minutes
        total_seconds = from_time.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        # Format as HH:MM
        jsonstarttime = f"{int(hours):02}:{int(minutes):02}"
    
    if isinstance(to_time,str):
        jsonendtime = ":".join(to_time.split(":")[:2]) 
        #jsonendtime = to_time
    else:
        # Convert timedelta to hours and minutes
        total_seconds = to_time.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        # Format as HH:MM
        jsonendtime = f"{int(hours):02}:{int(minutes):02}"

    #logging.debug(f"whatsup {jsondate}, {jsonstarttime}, {jsonendtime}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {decrypted_value}"
    }
    data = {
        "countryCode": "+91",
        "fullPhoneNumber": f"+91{mobile}",
        "callbackData": "some text here",
        "type": "Template",
        "template": {
            "name": f"{whatsupsettings.template}",
            "languageCode": "en",
            "headerValues": [
                booking_status
            ],            
            "bodyValues": [
                name,
                hall_name,
                jsondate,
                jsonstarttime,
                jsonendtime
            ]
        }        
    }
    try:
        response = requests.post(whatsupsettings.url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        #logging.debug(f"******************whatsup message sent {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        #logging.debug(f"&&&&&&&&&&&&&whatsup message sent error  {response.json()}, {str(e)}")
        frappe.throw(f"Error sending WhatsApp message: {str(e)}")








# @frappe.whitelist(allow_guest=True)  # Make sure this decorator is present
# def update_booking_status(booking_id, status):
#     """Update booking status"""

#     if not frappe.db.exists("booking", booking_id):
#         frappe.throw(_("Booking ID {} does not exist").format(booking_id))

#     booking = frappe.get_doc("booking", booking_id)
#     booking.booking_status = status
#     booking.save()
#     frappe.db.commit()

#     return {"status": "success", "message": f"Booking {status.lower()} successfully updated."}


@frappe.whitelist(allow_guest=True)
def update_booking_status(booking_id, status):
    """Update booking status (Approve or Cancel)"""

    # Check if the booking exists
    if not frappe.db.exists("booking", booking_id):
        frappe.throw(_("Booking ID {} does not exist").format(booking_id))

    booking = frappe.get_doc("booking", booking_id)
    
    # Only allow valid status updates
    if status not in ["Approved", "Cancelled"]:
        return {"status": "error", "message": _("Invalid status provided.")}

    if booking.booking_status == status:
        return {"status": "error", "message": _(f"Booking is already {status}.")}

    # Update the booking status
    booking.booking_status = status
    booking.save(ignore_permissions=True)  # Ignore permissions if needed
    frappe.db.commit()

    return {"status": "success", "message": _(f"Booking has been successfully {status.lower()}.")}


