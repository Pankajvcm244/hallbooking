// Copyright (c) 2025, Pankaj Sharma and contributors
// For license information, please see license.txt

frappe.ui.form.on('booking', {
    refresh: function (frm) {
        // Example: Show buttons only for users with the "VCM Room Approver" role
        if (frappe.user_roles.includes('VCM Room Approver')) {
            if (frm.doc.booking_status === 'Pending') {
                frm.add_custom_button(__('Approve'), function () {
                    frappe.call({
                        method: "hallbooking.hallbooking_custom.doctype.booking.booking.approve_booking",
                            args: {
                                booking_id: frm.doc.name
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.msgprint(__('Booking has been successfully approved.'));
                                    frm.reload_doc(); // Reload the form to reflect changes
                                } else {
                                    frappe.msgprint(__('Failed to approve the booking.'));
                                }
                            }                        
                    });
                });
            }
        }
        if (frm.doc.booking_status != 'Cancelled') {
            frm.add_custom_button(__('Cancel Booking'), function () {
                frappe.confirm(
                    __('Are you sure you want to cancel this booking?'),
                    function () {
                        // Call the server-side method to cancel the booking
                        frappe.call({
                            method: "hallbooking.hallbooking_custom.doctype.booking.booking.cancel_booking",
                            args: {
                                booking_id: frm.doc.name
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.msgprint(__('Booking has been successfully cancelled.'));
                                    frm.reload_doc(); // Reload the form to reflect changes
                                } else {
                                    frappe.msgprint(__('Failed to cancel the booking.'));
                                }
                            }
                        });
                    }
                );
            }).addClass('btn-danger'); // Make the button red
        }
        // Example: Show a button to create recurring bookings
        if (frm.doc.docstatus === 1 && frm.doc.recurring) {
            frm.add_custom_button(__('Create Recurring Bookings'), function () {
                //frm.trigger('create_recurring');
            });
        }
    },
    hall_name: function (frm) {
        if (frm.doc.hall_name) {
            // Fetch room details
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Halls',
                    name: frm.doc.hall_name, // Hall name selected in the form
                },
                callback: function (r) {
                    if (r.message) {
                        let room = r.message;
                        // Set fetched values into the booking form
                        frm.set_value('location', room.location); // Assuming `location` is a field in vcmroom
                        frm.set_value('people_capacity', room.people_capacity); // Assuming `seating_capacity` exists
                        frm.set_value('sound_system_available', room.sound_system_available); // Example field
                        frm.set_value('tv_available', room.tv_available);
                        frm.set_value('hall_label', room.room_name);
                        frm.set_value('additional_seating_available', room.additional_seating_available);
                        frm.set_value('restricted_only_via_approval', room.restricted_only_via_approval);
                    } else {
                        frappe.msgprint(__('Room details could not be fetched.'));
                    }
                }
            });
        } else {
            // Clear dynamically fetched fields if room_name is cleared
            frm.set_value('location', null);
            frm.set_value('people_capacity', null);
            frm.set_value('sound_system_available', null);
            frm.set_value('tv_available', null);
            frm.set_value('additional_seating_available', null);
            frm.set_value('hall_label', null);
            frm.set_value('restricted_only_via_approval', null);
        }
    },
    senior_devotee_name: function (frm) {
        if (frm.doc.senior_devotee_name) {
            // Fetch devotee details
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'roombookingdevotee',
                    name: frm.doc.senior_devotee_name, // Room name selected in the form
                },
                callback: function (r) {
                    if (r.message) {
                        let devotee = r.message;
                        // Set fetched values into the booking form
                        frm.set_value('booking_status', 'Approved');
                        frm.set_value('senior_devotee_email', devotee.devotee_email);
                        frm.set_value('vcm_devotee_name', devotee.devotee_name);
                    } else {
                        frappe.msgprint(__('Devotee details could not be fetched.'));
                    }
                }
            });
        } else {
            // Clear dynamically fetched fields if room_name is cleared
            frm.set_value('booking_status', 'Pending');
            frm.set_value('senior_devotee_email', null);
            frm.set_value('vcm_devotee_name', null);
        }
    },
    setup: function (frm) {
        frm.set_query('hall_name', function () {
            return {
                filters: {
                    status: 'Available' // Only show available rooms
                }
            };
        });
    },
    create_recurring: function (frm) {
        frappe.call({
            method: "path.to.script.create_recurring_conference_bookings",
            args: {
                room_booking_id: frm.doc.name,
            },
            callback: function (r) {
                if (r.message) {
                    frappe.msgprint(r.message);
                    frm.reload_doc();
                }
            }
        });
    },
    send_whatsapp: function(frm) {
        frappe.call({
            method: "vcmroombooking.vcmbooking_custom.doctype.roombookingvcm.roombookingvcm.send_whatsapp_message",
            args: {
                phone_number: frm.doc.submitter_mobile,
                template_id: "ERPNext1",  // Replace with actual ID
                params: { name: frm.doc.customer_name } // Adjust based on template
            },
            callback: function(response) {
                frappe.msgprint("WhatsApp message sent successfully!");
            }
        });
    },
    onload: function(frm) {
        if (frm.doc.restricted_only_via_approval === 'Yes') {
                frm.doc.booking_status === 'Pending';
        } else {
                frm.doc.booking_status === 'Approved';
            
        }
        frm.fields_dict['from_time'].picker_options = {
            enableSeconds: false,
        },
        frm.fields_dict['to_time'].picker_options = {
            enableSeconds: false,
        }
    }
});


