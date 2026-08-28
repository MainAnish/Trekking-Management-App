# 🥾 TrekMate – Trekking Management System

A Flask-based web application for managing trekking activities. The system provides separate dashboards and functionalities for **Admin**, **Trek Staff**, and **Users (Trekkers)**, enabling efficient trek management, booking, participant tracking, and staff approval.

---

## 📌 Features

### Admin
- Secure Login
- Dashboard with Statistics
- Add/Edit/Delete Treks
- Manage Users
- Approve/Reject Trek Staff
- Assign Staff to Treks
- Manage Bookings
- Blacklist/Unblacklist Users
- Search Functionality

### Trek Staff
- Secure Login
- Dashboard
- View Assigned Treks
- Update Trek Information
- View Participants
- Trek Details

### User (Trekker)
- Registration & Login
- Browse Available Treks
- Search Treks
- View Trek Details
- Book Trek
- Cancel Booking
- View Booking History
- Update Profile

---

## 🛠 Technologies Used

### Backend
- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- Bootstrap Icons
- Jinja2 Templates

### Database
- SQLite

---

## 📂 Project Structure

```
TrekMate/
│
├── app.py
├── config.py
├── models.py
├── requirements.txt
│
├── auth.py
├── admin.py
├── staff.py
├── user.py
│
├── database/
│     └── trekking.db
│
├── static/
│     ├── css/
│     ├── images/
│     └── js/
│
├── templates/
│     ├── admin/
│     ├── staff/
│     ├── user/
│     ├── login.html
│     ├── register_user.html
│     ├── register_staff.html
│     ├── base.html
│     ├── base_dashboard.html
│     ├── 403.html
│     ├── 404.html
│     └── 500.html
│
└── README.md
```

---

## 👥 User Roles

### Admin

- Manage Treks
- Manage Staff
- Manage Users
- Approve Staff
- Assign Staff
- View Bookings

---

### Trek Staff

- View Assigned Treks
- Update Trek Status
- View Participants

---

### User

- Register/Login
- Browse Treks
- Book Trek
- Cancel Booking
- View History
- Update Profile

---

## 🗄 Database Tables

- User
- Trek
- Booking

---

## 🔐 Default Admin Credentials

Email

```
admin@example.com
```

Password

```
admin123
```

---

## ▶ Installation

### Clone Project

```bash
git clone <repository-link>
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Project

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

## 📸 Screenshots

Add screenshots of:

- Login
- Register User
- Register Staff
- Admin Dashboard
- Manage Treks
- Staff Dashboard
- User Dashboard
- Booking
- History
- Profile

---

## ✨ Future Enhancements

- Trek Image Upload
- Email Notifications
- PDF Booking Receipt
- Trek Reviews & Ratings
- Dashboard Charts
- Online Payment Integration

---

## 👨‍💻 Developed By

**Anish Kumar**

Flask + SQLite Project
