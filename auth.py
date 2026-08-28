from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User

auth = Blueprint("auth", __name__)


# =====================================
# LOGIN
# =====================================
@auth.route("/", methods=["GET", "POST"])
@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:

        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))

        elif current_user.role == "staff":
            return redirect(url_for("staff.dashboard"))

        else:
            return redirect(url_for("user.dashboard"))

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            # Blacklist Check
            if user.blacklisted:
                flash("Your account has been blacklisted.", "danger")
                return redirect(url_for("auth.login"))

            # Staff Approval Check
            if user.role == "staff" and not user.approved:
                flash("Your account is waiting for Admin approval.", "warning")
                return redirect(url_for("auth.login"))

            login_user(user)

            flash("Login Successful!", "success")

            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))

            elif user.role == "staff":
                return redirect(url_for("staff.dashboard"))

            else:
                return redirect(url_for("user.dashboard"))

        flash("Invalid Email or Password.", "danger")

    return render_template("login.html")


# =====================================
# USER REGISTRATION
# =====================================
@auth.route("/register/user", methods=["GET", "POST"])
def register_user():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register_user"))

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register_user"))

        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            role="user",
            approved=True,
            blacklisted=False
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful. Please Login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register_user.html")


# =====================================
# STAFF REGISTRATION
# =====================================
@auth.route("/register/staff", methods=["GET", "POST"])
def register_staff():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register_staff"))

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register_staff"))

        staff = User(
            name=name,
            email=email,
            phone=phone,
            password=generate_password_hash(password),
            role="staff",
            approved=False,
            blacklisted=False
        )

        db.session.add(staff)
        db.session.commit()

        flash(
            "Registration Successful. Wait for Admin Approval.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("register_staff.html")


# =====================================
# LOGOUT
# =====================================
@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged Out Successfully.", "success")

    return redirect(url_for("auth.login"))