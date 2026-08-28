from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from models import db, User, Trek, Booking

admin = Blueprint("admin", __name__)


# =====================================
# ADMIN ACCESS DECORATOR
# =====================================
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if current_user.role != "admin":
            flash("Access Denied!", "danger")
            return redirect(url_for("auth.login"))

        return func(*args, **kwargs)

    return wrapper


# =====================================
# ADMIN DASHBOARD
# =====================================
@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():

    total_users = User.query.filter_by(role="user").count()

    total_staff = User.query.filter_by(role="staff").count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    pending_staff = User.query.filter_by(
        role="staff",
        approved=False
    ).count()

    recent_bookings = Booking.query.order_by(
        Booking.booking_date.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        pending_staff=pending_staff,
        recent_bookings=recent_bookings
    )


# =====================================
# VIEW ALL TREKS
# =====================================
@admin.route("/treks")
@login_required
@admin_required
def manage_treks():

    treks = Trek.query.order_by(Trek.id.desc()).all()

    return render_template(
        "admin/manage_treks.html",
        treks=treks
    )


# =====================================
# ADD NEW TREK
# =====================================
@admin.route("/treks/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_trek():

    staff_members = User.query.filter_by(
        role="staff",
        approved=True,
        blacklisted=False
    ).all()

    if request.method == "POST":

        trek = Trek(

            trek_name=request.form["trek_name"],

            location=request.form["location"],

            difficulty=request.form["difficulty"],

            duration=int(request.form["duration"]),

            available_slots=int(request.form["available_slots"]),

            description=request.form["description"],

            start_date=datetime.strptime(
                request.form["start_date"],
                "%Y-%m-%d"
            ).date(),

            end_date=datetime.strptime(
                request.form["end_date"],
                "%Y-%m-%d"
            ).date(),

            status=request.form["status"],

            staff_id=request.form["staff_id"]
            if request.form["staff_id"]
            else None

        )

        db.session.add(trek)
        db.session.commit()

        flash("Trek Added Successfully.", "success")

        return redirect(url_for("admin.manage_treks"))

    return render_template(
        "admin/add_trek.html",
        staff_members=staff_members
    )
    # =====================================
# EDIT TREK
# =====================================
@admin.route("/treks/edit/<int:trek_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    staff_members = User.query.filter_by(
        role="staff",
        approved=True,
        blacklisted=False
    ).all()

    if request.method == "POST":

        trek.trek_name = request.form["trek_name"]

        trek.location = request.form["location"]

        trek.difficulty = request.form["difficulty"]

        trek.duration = int(request.form["duration"])

        trek.available_slots = int(request.form["available_slots"])

        trek.description = request.form["description"]

        trek.start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()

        trek.end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()

        trek.status = request.form["status"]

        staff_id = request.form.get("staff_id")

        trek.staff_id = int(staff_id) if staff_id else None

        db.session.commit()

        flash("Trek Updated Successfully.", "success")

        return redirect(url_for("admin.manage_treks"))

    return render_template(
        "admin/edit_trek.html",
        trek=trek,
        staff_members=staff_members
    )


# =====================================
# DELETE TREK
# =====================================
@admin.route("/treks/delete/<int:trek_id>")
@login_required
@admin_required
def delete_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)

    db.session.commit()

    flash("Trek Deleted Successfully.", "success")

    return redirect(url_for("admin.manage_treks"))


# =====================================
# VIEW ALL STAFF
# =====================================
@admin.route("/staff")
@login_required
@admin_required
def manage_staff():

    staff_members = User.query.filter_by(
        role="staff"
    ).order_by(User.id.desc()).all()

    return render_template(
        "admin/manage_staff.html",
        staff_members=staff_members
    )


# =====================================
# APPROVE STAFF
# =====================================
@admin.route("/staff/approve/<int:staff_id>")
@login_required
@admin_required
def approve_staff(staff_id):

    staff = User.query.get_or_404(staff_id)

    if staff.role != "staff":

        flash("Invalid Staff.", "danger")

        return redirect(url_for("admin.manage_staff"))

    staff.approved = True

    db.session.commit()

    flash("Staff Approved Successfully.", "success")

    return redirect(url_for("admin.manage_staff"))


# =====================================
# BLACKLIST STAFF
# =====================================
@admin.route("/staff/blacklist/<int:staff_id>")
@login_required
@admin_required
def blacklist_staff(staff_id):

    staff = User.query.get_or_404(staff_id)

    if staff.role != "staff":

        flash("Invalid Staff.", "danger")

        return redirect(url_for("admin.manage_staff"))

    staff.blacklisted = True

    db.session.commit()

    flash("Staff Blacklisted Successfully.", "warning")

    return redirect(url_for("admin.manage_staff"))


# =====================================
# REMOVE STAFF FROM BLACKLIST
# =====================================
@admin.route("/staff/unblacklist/<int:staff_id>")
@login_required
@admin_required
def unblacklist_staff(staff_id):

    staff = User.query.get_or_404(staff_id)

    if staff.role != "staff":

        flash("Invalid Staff.", "danger")

        return redirect(url_for("admin.manage_staff"))

    staff.blacklisted = False

    db.session.commit()

    flash("Staff Activated Successfully.", "success")

    return redirect(url_for("admin.manage_staff"))


# =====================================
# ASSIGN STAFF TO TREK
# =====================================
@admin.route("/assign/<int:trek_id>", methods=["GET", "POST"])
@login_required
@admin_required
def assign_staff(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    staff_members = User.query.filter_by(
        role="staff",
        approved=True,
        blacklisted=False
    ).all()

    if request.method == "POST":

        trek.staff_id = int(request.form["staff_id"])

        db.session.commit()

        flash("Staff Assigned Successfully.", "success")

        return redirect(url_for("admin.manage_treks"))

    return render_template(
        "admin/assign_staff.html",
        trek=trek,
        staff_members=staff_members
    )
    # =====================================
# MANAGE USERS
# =====================================
@admin.route("/users")
@login_required
@admin_required
def manage_users():

    users = User.query.filter_by(
        role="user"
    ).order_by(User.id.desc()).all()

    return render_template(
        "admin/manage_users.html",
        users=users
    )


# =====================================
# BLACKLIST USER
# =====================================
@admin.route("/users/blacklist/<int:user_id>")
@login_required
@admin_required
def blacklist_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.role != "user":

        flash("Invalid User.", "danger")

        return redirect(url_for("admin.manage_users"))

    user.blacklisted = True

    db.session.commit()

    flash("User Blacklisted Successfully.", "warning")

    return redirect(url_for("admin.manage_users"))


# =====================================
# REMOVE USER FROM BLACKLIST
# =====================================
@admin.route("/users/unblacklist/<int:user_id>")
@login_required
@admin_required
def unblacklist_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.role != "user":

        flash("Invalid User.", "danger")

        return redirect(url_for("admin.manage_users"))

    user.blacklisted = False

    db.session.commit()

    flash("User Activated Successfully.", "success")

    return redirect(url_for("admin.manage_users"))


# =====================================
# VIEW ALL BOOKINGS
# =====================================
@admin.route("/bookings")
@login_required
@admin_required
def manage_bookings():

    bookings = Booking.query.order_by(
        Booking.booking_date.desc()
    ).all()

    return render_template(
        "admin/manage_bookings.html",
        bookings=bookings
    )


# =====================================
# SEARCH
# =====================================
@admin.route("/search")
@login_required
@admin_required
def search():

    query = request.args.get("query", "").strip()

    users = User.query.filter(
        User.name.ilike(f"%{query}%")
    ).all()

    staff_members = User.query.filter(
        User.role == "staff",
        User.name.ilike(f"%{query}%")
    ).all()

    treks = Trek.query.filter(
        Trek.trek_name.ilike(f"%{query}%")
    ).all()

    return render_template(
        "admin/search.html",
        query=query,
        users=users,
        staff_members=staff_members,
        treks=treks
    )


# =====================================
# VIEW TREK DETAILS
# =====================================
@admin.route("/treks/<int:trek_id>")
@login_required
@admin_required
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    participants = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        "admin/trek_details.html",
        trek=trek,
        participants=participants
    )


# =====================================
# CHANGE TREK STATUS
# =====================================
@admin.route("/treks/status/<int:trek_id>/<status>")
@login_required
@admin_required
def change_trek_status(trek_id, status):

    trek = Trek.query.get_or_404(trek_id)

    allowed_status = [
        "Pending",
        "Approved",
        "Open",
        "Closed",
        "Completed"
    ]

    if status not in allowed_status:

        flash("Invalid Status.", "danger")

        return redirect(url_for("admin.manage_treks"))

    trek.status = status

    db.session.commit()

    flash("Trek Status Updated.", "success")

    return redirect(url_for("admin.manage_treks"))


# =====================================
# DELETE BOOKING
# =====================================
@admin.route("/booking/delete/<int:booking_id>")
@login_required
@admin_required
def delete_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    db.session.delete(booking)

    db.session.commit()

    flash("Booking Deleted Successfully.", "success")

    return redirect(url_for("admin.manage_bookings"))