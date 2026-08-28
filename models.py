from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager

# Initialize SQLAlchemy
db = SQLAlchemy()

# Initialize Flask-Login
login_manager = LoginManager()


# ==========================
# USER MODEL
# ==========================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    role = db.Column(db.String(20), nullable=False)
    # admin
    # staff
    # user

    approved = db.Column(db.Boolean, default=False)

    blacklisted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_treks = db.relationship(
        "Trek",
        backref="assigned_staff",
        lazy=True
    )

    bookings = db.relationship(
        "Booking",
        backref="user",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.name}>"



# ==========================
# TREK MODEL
# ==========================
class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    trek_name = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    difficulty = db.Column(
        db.String(20),
        nullable=False
    )
    # Easy
    # Moderate
    # Hard

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    available_slots = db.Column(
        db.Integer,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )
    # Pending
    # Approved
    # Open
    # Closed
    # Completed

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Trek {self.trek_name}>"



# ==========================
# BOOKING MODEL
# ==========================
class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    status = db.Column(
        db.String(20),
        default="Booked"
    )
    # Booked
    # Cancelled
    # Completed

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Booking {self.id}>"



# ==========================
# FLASK LOGIN
# ==========================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))