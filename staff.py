from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

from models import db, User, Trek, Booking

staff = Blueprint("staff", __name__)


# =====================================
# STAFF ACCESS DECORATOR
# =====================================
def staff_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if current_user.role != "staff":
            flash("Access Denied!", "danger")
            return redirect(url_for("auth.login"))

        if not current_user.approved:
            flash("Your account is awaiting admin approval.", "warning")
            return redirect(url_for("auth.login"))

        if current_user.blacklisted:
            flash("Your account has been blacklisted.", "danger")
            return redirect(url_for("auth.login"))

        return func(*args, **kwargs)

    return wrapper


# =====================================
# STAFF DASHBOARD
# =====================================
@staff.route("/dashboard")
@login_required
@staff_required
def dashboard():

    assigned_treks = Trek.query.filter_by(
        staff_id=current_user.id
    ).all()

    total_treks = len(assigned_treks)

    total_participants = 0

    open_treks = 0

    for trek in assigned_treks:

        total_participants += Booking.query.filter_by(
            trek_id=trek.id
        ).count()

        if trek.status == "Open":
            open_treks += 1

    return render_template(
        "staff/dashboard.html",
        treks=assigned_treks,
        total_treks=total_treks,
        total_participants=total_participants,
        open_treks=open_treks
    )


# =====================================
# VIEW ASSIGNED TREKS
# =====================================
@staff.route("/treks")
@login_required
@staff_required
def assigned_treks():

    treks = Trek.query.filter_by(
        staff_id=current_user.id
    ).all()

    return render_template(
        "staff/assigned_treks.html",
        treks=treks
    )


# =====================================
# VIEW PARTICIPANTS OF A TREK
# =====================================
@staff.route("/participants/<int:trek_id>")
@login_required
@staff_required
def participants(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    # Security check
    if trek.staff_id != current_user.id:

        flash("You are not assigned to this trek.", "danger")

        return redirect(url_for("staff.dashboard"))

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        "staff/participants.html",
        trek=trek,
        bookings=bookings
    )
from flask import request
from datetime import datetime


# =====================================
# UPDATE TREK
# =====================================
@staff.route("/trek/update/<int:trek_id>", methods=["GET", "POST"])
@login_required
@staff_required
def update_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    # Staff can update only assigned trek
    if trek.staff_id != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.dashboard"))

    if request.method == "POST":

        trek.available_slots = int(request.form["available_slots"])

        trek.status = request.form["status"]

        db.session.commit()

        flash("Trek Updated Successfully.", "success")

        return redirect(url_for("staff.assigned_treks"))

    return render_template(
        "staff/update_trek.html",
        trek=trek
    )


# =====================================
# START TREK
# =====================================
@staff.route("/trek/start/<int:trek_id>")
@login_required
@staff_required
def start_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.dashboard"))

    trek.status = "Open"

    db.session.commit()

    flash("Trek Started Successfully.", "success")

    return redirect(url_for("staff.assigned_treks"))


# =====================================
# CLOSE TREK
# =====================================
@staff.route("/trek/close/<int:trek_id>")
@login_required
@staff_required
def close_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.dashboard"))

    trek.status = "Closed"

    db.session.commit()

    flash("Trek Closed Successfully.", "success")

    return redirect(url_for("staff.assigned_treks"))


# =====================================
# COMPLETE TREK
# =====================================
@staff.route("/trek/complete/<int:trek_id>")
@login_required
@staff_required
def complete_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.dashboard"))

    trek.status = "Completed"

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    for booking in bookings:
        booking.status = "Completed"

    db.session.commit()

    flash("Trek Completed Successfully.", "success")

    return redirect(url_for("staff.assigned_treks"))


# =====================================
# VIEW TREK DETAILS
# =====================================
@staff.route("/trek/<int:trek_id>")
@login_required
@staff_required
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.dashboard"))

    participants = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    total_participants = len(participants)

    return render_template(
        "staff/trek_details.html",
        trek=trek,
        participants=participants,
        total_participants=total_participants
    )


# =====================================
# CHANGE AVAILABLE SLOTS
# =====================================
@staff.route("/trek/slots/<int:trek_id>", methods=["POST"])
@login_required
@staff_required
def update_slots(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.dashboard"))

    slots = int(request.form["available_slots"])

    if slots < 0:
        flash("Slots cannot be negative.", "danger")
        return redirect(url_for("staff.update_trek", trek_id=trek.id))

    trek.available_slots = slots

    db.session.commit()

    flash("Available Slots Updated Successfully.", "success")

    return redirect(url_for("staff.update_trek", trek_id=trek.id))


# =====================================
# CHANGE TREK STATUS
# =====================================
@staff.route("/trek/status/<int:trek_id>", methods=["POST"])
@login_required
@staff_required
def update_status(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != current_user.id:
        flash("Access Denied!", "danger")
        return redirect(url_for("staff.dashboard"))

    status = request.form["status"]

    allowed_status = [
        "Open",
        "Closed",
        "Completed"
    ]

    if status not in allowed_status:
        flash("Invalid Status.", "danger")
        return redirect(url_for("staff.update_trek", trek_id=trek.id))

    trek.status = status

    if status == "Completed":

        bookings = Booking.query.filter_by(
            trek_id=trek.id
        ).all()

        for booking in bookings:
            booking.status = "Completed"

    db.session.commit()

    flash("Trek Status Updated Successfully.", "success")

    return redirect(url_for("staff.update_trek", trek_id=trek.id))