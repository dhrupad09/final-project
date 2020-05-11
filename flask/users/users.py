from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, has_role
from users.forms import RegisterForm, LoginForm, ContentForm
from users.models import User, Role, Techademy

users_bp = Blueprint("users", __name__, template_folder="templates")


@users_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.errors)
        if form.password.data == form.confirm_password.data:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=generate_password_hash(form.password.data, method='sha256')
            )
            db.session.add(user)
            role = Role.query.filter_by(name="Generic").first()
            if role is not None:
                user.roles.append(role)
            try:
                db.session.commit()
                flash("Successfully registered")
            except IntegrityError as err:
                db.session.rollback()
                if "UNIQUE constraint failed" in str(err):
                    flash("error, username already exists (%s)" % form.username.data)
                else:
                    flash("unknown error adding user")
        else:
            flash("Passwords don't match")
    return render_template("register.html", form=form, title="Register")


@users_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Please check your login details and try again.')
            return redirect(url_for('users.login'))  # if user doesn't exist or password is wrong, reload the page
        login_user(user)
        return redirect(url_for('users.home'))
    return render_template("login.html", form=form, title="Login")


@users_bp.route('/home')
@login_required
def home():
    return render_template("home.html", title="Home")


@users_bp.route('/admin', methods=['GET', 'POST'])
@has_role("Admin")
def admin():
    form = ContentForm()
    if form.validate_on_submit():
        techademy = Techademy(
            python=form.python.data,
            github=form.github.data,
            java=form.java.data
        )
        db.session.add(techademy)
        try:
            db.session.commit()
            flash("Successfully Added")
        except IntegrityError as err:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(err):
                flash("error")
            else:
                flash("unknown error adding contents")
    else:
        flash("Add Contents")
    return render_template("admin.html", form=form, title="Admin")


@users_bp.route('/python')
@login_required
def python():
    return render_template("python.html", python=python, title="Python")


@users_bp.route('/github')
@login_required
def github():
    return render_template("github.html", github=github, title="Github")


@users_bp.route('/java')
@login_required
def java():
    return render_template("java.html", java=java, title="JavaScript")


@users_bp.route('/compiler')
@login_required
def compiler():
    return render_template("compiler.html", title="Compiler")


@users_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("users.login"))




