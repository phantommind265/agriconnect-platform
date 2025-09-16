from functools import wraps
import sqlite3
import os
import config
from config import DB_PATH
from flask_login import login_user, logout_user, login_required, current_user
#from app.models.user_model import get_user_by_username
from agriplatform.models.models import User
#from app.models.models import User, db
from agriplatform.forms.register_form import RegisterForm, ForgotPasswordForm, ResetPasswordForm
from agriplatform.forms.login_form import LoginForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from agriplatform.utils.logger import log_event
from agriplatform.utils.translator import t
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import secrets
import hashlib
from flask_mail import Message, Mail

UPLOAD_FOLDER = os.path.join("agriplatform", "static", "uploads", "profile_pic")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
auth_bp = Blueprint("auth", __name__)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/farmer/dashboard')
def farmer_dashboard():
    if current_user.role != 'farmer':
        flash("Access denied")
        return redirect(url_for('auth.login'))
    return render_template('dashboards/farmer_dashboard.html')


@auth_bp.route('/extension/dashboard')
@login_required
def extension_dashboard():
    if current_user.role != 'extension_worker':
        flash("Access denied")
        return redirect(url_for('auth.login'))
    return render_template('dashboards/extension_worker.html')

@auth_bp.route('/admin/dashboard')
def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access denied")
        return redirect(url_for('auth.login'))
    return render_template('dashboards/admin_dashboard.html')

#Home route
@auth_bp.route("/dashboard")
def home():
    return render_template("home_mobile.html")

#testing
@auth_bp.route('/testing')
def testing():
    return render_template('farmer_dashboard.html')

#testing two
@auth_bp.route('/testingtwo')
def testingtwo():
    return render_template('new_advisory.html')

#help route
@auth_bp.route('/help')
def help():
    return render_template('FAQ.html')

#dashboard route
@auth_bp.route("/")
def dashboard():
    return render_template("home.html")

#about route
@auth_bp.route('/about')
def about_page():
    return render_template("about_page.html")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash(t("access_denied"), "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

#login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()

        user = User.find_by_username(username)

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)

            flash("Login successful!", "success")

            # Redirect based on role
            if user.role == "farmer":
                return redirect(url_for("auth.farmer_dashboard"))
            elif user.role == "extension_worker":
                return redirect(url_for("auth.extension_dashboard"))
            elif user.role == "admin":
                return redirect(url_for("auth.admin_dashboard"))
            else:
                flash("Unknown role assigned. Contact admin.", "danger")
                return redirect(url_for("auth.login"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/lang/<code>")
def set_language(code):
    if code in ["en", "ny"]:
        session["lang"] = code
    return redirect(request.referrer or url_for('auth.home'))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET reset_token = ? WHERE id = ?", (token, user[0]))
            conn.commit()
            conn.close()

            reset_link = url_for('auth.reset_password', token=token, _external=True)
            msg = Message("AgriConnect Password Reset", recipients=[email])
            msg.body = f"Hello, \n\nYou requested a password reset. Click the link below to reset your password:\n\n{reset_link}\n\nIf you didn't request this, ignore this email."
            email.send(msg)

            flash("Password reset link has been sent to your email.", "success")
        else:
            flash("Email not found.", "danger")

        return redirect(url_for("auth_bp.forgot_password"))

    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()
        crop = form.crop.data.strip()
        district = form.district.data
        role = form.role.data
        language = form.language.data
        email = form.email.data.strip()

        file = form.profile_pic.data
        filename = "default.png"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # check if username or email exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        existing = cursor.fetchone()
        if existing:
            flash("Username or email already taken!", "danger")
            conn.close()
            return render_template("auth/register.html", form=form)

        # insert new user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, crop, district, role, language, email, profile_pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, hashed_password, crop, district, role, language, email, filename),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        # auto-login after registration
        new_user = User.get(user_id)
        login_user(new_user)

        flash("Account created successfully!", "success")

        # redirect based on role
        if role == "farmer":
            return redirect(url_for("auth.farmer_dashboard"))
        elif role == "extension_worker":
            return redirect(url_for("auth.extension_dashboard"))
        elif role == "admin":
            return redirect(url_for("auth.admin_dashboard"))
        else:
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    form = ResetPasswordForm()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE reset_token = ?", (token,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for("auth_bp.login"))
    
    if form.validate_on_submit():
        password = form.password.data.strip()
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ?, reset_token = NULL WHERE id = ?", (hashed_password, user[0]))
        conn.commit()
        conn.close()

        flash("Your password has been reset successfully.", "success")
        return redirect(url_for("auth_bp.login"))

    return render_template("reset_password.html", form=form)


@auth_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        try:
            msg = Message(subject=f"[AgrConnect Contact[ {subject}",
                          recipients=[config["MAIL_USERNAME"]])
            msg.body = f"""
            New message from AgriConnect Contact Foem:

            Name: {name}
            Email: {email}
            Subject: {subject}

            Message: {message}
            """
            Mail.send(msg)
            flash('Your message has been sent successfully', 'success')
        except Exception as e:
            flash(f'Error sending message: {e}', 'danger')
        return redirect(url_for('contact'))
    return render_template('about.html')
