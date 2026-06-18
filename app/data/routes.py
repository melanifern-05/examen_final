from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user

from ..forms import ImportCsvForm
from .services import import_sales_csv

data_bp = Blueprint("data", __name__)


@data_bp.route("/importar", methods=["GET", "POST"])
@login_required
def importar():
    if current_user.role != "admin":
        flash("Solo el administrador puede importar datos.", "danger")
        return redirect(url_for("dashboard.ejecutivo"))

    form = ImportCsvForm()
    mensaje = None
    if form.validate_on_submit():
        path = current_app.root_path + "/../ventas_supermercado.csv"
        mensaje = import_sales_csv(path)
        if "ERROR" in mensaje:
            flash(mensaje, "danger")
        else:
            flash(mensaje, "success")
        return redirect(url_for("data.importar"))

    return render_template("import_csv.html", form=form)
