from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import current_user, login_required, login_user, logout_user
from . import login_manager 
from .models import User
from .forms import LoginForm, RegisterForm
from . import db_manager as db
from .helper_role import notify_identity_changed
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound



auth_bp = Blueprint(
    "auth_bp", __name__, template_folder="templates", static_folder="static"
)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main_bp.init"))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        plain_text_password = form.password.data

        user = load_user(email)

        print(f"Hash is {user.password} and password is {plain_text_password}")

        if user and check_password_hash(user.password, plain_text_password):
            login_user(user)
            notify_identity_changed()
            flash('Logged in successfully.', "success")
            return redirect(url_for("main_bp.init"))

        flash("Credenciales incorrectas. Por favor, inténtelo de nuevo.", "error")
        return redirect(url_for("auth_bp.login"))

    return render_template('login.html', form = form)


@login_manager.user_loader
def load_user(email):
    if email is not None:
        try:
            user_or_none = db.session.query(User).filter(User.email == email).one()
            return user_or_none
        except (NoResultFound, MultipleResultsFound):
            return None
    return None



@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth_bp.login"))




@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main_bp.init"))

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        name = form.name.data
        plain_text_password = form.password.data

     
        existing_user = db.session.query(User).filter(User.email == email).first()
        if existing_user:
            flash('El correo electrónico ya está registrado. Inicia sesión en lugar de registrarte.', 'warning')
            return redirect(url_for("auth_bp.login"))

     
        hashed_password = generate_password_hash(plain_text_password, method='scrypt:32768:8:1')
        new_user = User(name = name, email=email, password=hashed_password, role = "wanner")
        db.session.add(new_user)
        db.session.commit()

        flash('Registro exitoso. Inicia sesión ahora.', 'success')
        return redirect(url_for("auth_bp.login"))

    return render_template('register.html', form=form)


@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)