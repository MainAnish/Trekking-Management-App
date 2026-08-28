from flask import Flask, redirect, url_for, render_template
from werkzeug.security import generate_password_hash

from config import Config
from models import db, login_manager, User

# Import Blueprints
from auth import auth
from admin import admin
from staff import staff
from user import user


# =====================================
# CREATE FLASK APP
# =====================================
app = Flask(__name__)
app.config.from_object(Config)


# =====================================
# INITIALIZE EXTENSIONS
# =====================================
db.init_app(app)
login_manager.init_app(app)

login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to continue."
login_manager.login_message_category = "warning"


# =====================================
# REGISTER BLUEPRINTS
# =====================================
app.register_blueprint(auth)

app.register_blueprint(admin, url_prefix="/admin")

app.register_blueprint(staff, url_prefix="/staff")

app.register_blueprint(user, url_prefix="/user")


# =====================================
# HOME PAGE
# =====================================
@app.route("/")
def home():
    return redirect(url_for("auth.login"))


# =====================================
# CREATE DEFAULT ADMIN
# =====================================
def create_default_admin():

    admin = User.query.filter_by(
        email="admin@example.com"
    ).first()

    if not admin:

        admin = User(
            name="Administrator",
            email="admin@example.com",
            password=generate_password_hash("admin123"),
            phone="9999999999",
            role="admin",
            approved=True,
            blacklisted=False
        )

        db.session.add(admin)
        db.session.commit()

        print("✓ Default Admin Created")

    else:

        print("✓ Admin Already Exists")


# =====================================
# ERROR HANDLERS
# =====================================
@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


# =====================================
# MAIN
# =====================================
if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        create_default_admin()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )