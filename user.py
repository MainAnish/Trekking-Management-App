from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

from models import db, User, Trek, Booking

user = Blueprint("user", __name__)


# =====================================
# USER ACCESS DECORATOR
# =====================================
def user_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if current_user.role != "user":
            flash("Access Denied!", "danger")
            return redirect(url_for("auth.login"))

        if current_user.blacklisted:
            flash("Your account has been blacklisted.", "danger")
            return redirect(url_for("auth.login"))

        return func(*args, **kwargs)

    return wrapper


# =====================================
# USER DASHBOARD
# =====================================
@user.route("/dashboard")
@login_required
@user_required
def dashboard():

    total_bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).count()

    upcoming_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status="Booked"
    ).count()

    completed_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).count()

    recent_bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Booking.booking_date.desc()
    ).limit(5).all()

    return render_template(
        "user/dashboard.html",
        total_bookings=total_bookings,
        upcoming_bookings=upcoming_bookings,
        completed_bookings=completed_bookings,
        recent_bookings=recent_bookings
    )


# =====================================
# VIEW ALL TREKS
# =====================================
@user.route("/treks")
@login_required
@user_required
def view_treks():

    treks = Trek.query.filter(
        Trek.status == "Open"
    ).all()

    return render_template(
        "user/view_treks.html",
        treks=treks
    )


# =====================================
# SEARCH TREKS
# =====================================
@user.route("/search")
@login_required
@user_required
def search_treks():

    query = request.args.get("query", "").strip()

    treks = Trek.query.filter(
        Trek.trek_name.ilike(f"%{query}%"),
        Trek.status == "Open"
    ).all()

    return render_template(
        "user/view_treks.html",
        treks=treks,
        query=query
    )


# =====================================
# TREK DETAILS
# =====================================
@user.route("/trek/<int:trek_id>")
@login_required
@user_required
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    booked = Booking.query.filter_by(
        trek_id=trek.id,
        user_id=current_user.id
    ).first()

    return render_template(
        "user/trek_details.html",
        trek=trek,
        booked=booked
    )
    
from datetime import datetime
from werkzeug.security import generate_password_hash


# =====================================
# BOOK TREK
# =====================================
@user.route("/book/<int:trek_id>")
@login_required
@user_required
def book_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    # Trek should be open
    if trek.status != "Open":
        flash("This trek is not open for booking.", "danger")
        return redirect(url_for("user.view_treks"))

    # Prevent duplicate booking
    existing = Booking.query.filter_by(
        trek_id=trek.id,
        user_id=current_user.id
    ).first()

    if existing:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("user.trek_details", trek_id=trek.id))

    # Prevent overbooking
    booked_count = Booking.query.filter_by(
        trek_id=trek.id
    ).count()

    if booked_count >= trek.available_slots:
        flash("No slots available.", "danger")
        return redirect(url_for("user.view_treks"))

    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        booking_date=datetime.now(),
        status="Booked"
    )

    db.session.add(booking)
    db.session.commit()

    flash("Trek Booked Successfully.", "success")

    return redirect(url_for("user.my_bookings"))


# =====================================
# MY BOOKINGS
# =====================================
@user.route("/bookings")
@login_required
@user_required
def my_bookings():

    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Booking.booking_date.desc()
    ).all()

    return render_template(
        "user/my_bookings.html",
        bookings=bookings
    )


# =====================================
# BOOKING HISTORY
# =====================================
@user.route("/history")
@login_required
@user_required
def booking_history():

    history = Booking.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).all()

    return render_template(
        "user/history.html",
        history=history
    )


# =====================================
# CANCEL BOOKING
# =====================================
@user.route("/cancel/<int:booking_id>")
@login_required
@user_required
def cancel_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        flash("Access Denied.", "danger")
        return redirect(url_for("user.dashboard"))

    if booking.status == "Completed":
        flash("Completed trek cannot be cancelled.", "danger")
        return redirect(url_for("user.my_bookings"))

    db.session.delete(booking)

    db.session.commit()

    flash("Booking Cancelled Successfully.", "success")

    return redirect(url_for("user.my_bookings"))


# =====================================
# EDIT PROFILE
# =====================================
@user.route("/profile", methods=["GET", "POST"])
@login_required
@user_required
def profile():

    if request.method == "POST":

        current_user.name = request.form["name"]

        current_user.phone = request.form["phone"]

        password = request.form.get("password")

        if password:
            current_user.password = generate_password_hash(password)

        db.session.commit()

        flash("Profile Updated Successfully.", "success")

        return redirect(url_for("user.profile"))

    return render_template(
        "user/profile.html",
        user=current_user
    )