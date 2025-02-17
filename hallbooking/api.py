import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_halls():
    # Fetch records from the custom Doctype 'ERP Domain'
    records = frappe.get_all(
        'Halls',  # Doctype name
        fields=['name as id','hall_name', 'location','people_capacity','status','tv_available','sound_system_available','additional_seating_available','restricted_only_via_approval']  # Fields to fetch
    )
    return records





# @frappe.whitelist(allow_guest=True)
# def update_booking_status(booking_id, status):
#     """ Update booking status (Approve or Cancel) """
#     try:
#         booking = frappe.get_doc("booking", booking_id)
        
#         if status not in ["Approved", "Cancelled"]:
#             return {"status": "error", "message": _("Invalid status provided.")}

#         if booking.booking_status == status:
#             return {"status": "error", "message": _(f"Booking is already {status}.")}

#         booking.booking_status = status
#         booking.save()
#         frappe.db.commit()

#         return {"status": "success", "message": _(f"Booking has been successfully {status.lower()}.")}
#     except Exception as e:
#         return {"status": "error", "message": str(e)}



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






