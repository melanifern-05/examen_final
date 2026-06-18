from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from .. import db
from ..models import Usuario, BitacoraAcceso
from ..forms import LoginForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.ejecutivo"))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data.strip()).first()
        if user and user.activo and check_password_hash(user.password, form.password.data):
            login_user(user)
            log = BitacoraAcceso(
                user_id=user.id,
                evento="LOGIN",
                ip=request.remote_addr,
            )
            db.session.add(log)
            db.session.commit()
            return redirect(url_for("dashboard.ejecutivo"))
        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log = BitacoraAcceso(
        user_id=current_user.id,
        evento="LOGOUT",
        ip=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
