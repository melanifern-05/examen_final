from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func, extract

from .. import db
from ..models import Venta

dashboard_bp = Blueprint("dashboard", __name__)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _filtered_query(args):
    """Aplica filtros de URL a la query base de Venta."""
    q = Venta.query

    field_map = {
        "sucursal":    Venta.sucursal,
        "ciudad":      Venta.ciudad,
        "categoria":   Venta.categoria,
        "metodo_pago": Venta.metodo_pago,
    }

    for key, col in field_map.items():
        val = args.get(key, "").strip()
        if val:
            q = q.filter(col == val)

    anio = args.get("anio", "").strip()
    if anio:
        q = q.filter(extract("year", Venta.fecha) == int(anio))

    mes = args.get("mes", "").strip()
    if mes:
        q = q.filter(extract("month", Venta.fecha) == int(mes))

    return q


def _top_label(q, col):
    """Devuelve el label con mayor suma de total_venta."""
    row = (
        q.with_entities(col, func.sum(Venta.total_venta).label("s"))
        .group_by(col)
        .order_by(func.sum(Venta.total_venta).desc())
        .first()
    )
    return row[0] if row else "—"


def _executive_kpis(q):
    total_ventas   = q.with_entities(func.sum(Venta.total_venta)).scalar() or 0
    total_cantidad = q.with_entities(func.sum(Venta.cantidad)).scalar() or 0
    promedio       = q.with_entities(func.avg(Venta.total_venta)).scalar() or 0
    top_categoria  = _top_label(q, Venta.categoria)

    return [
        {
            "label": "Total de Ventas",
            "value": f"Bs {float(total_ventas):,.2f}",
            "icon":  "fa-dollar-sign",
            "tone":  "gold",
        },
        {
            "label": "Cantidad Vendida",
            "value": f"{int(total_cantidad):,}",
            "icon":  "fa-boxes-stacked",
            "tone":  "coffee",
        },
        {
            "label": "Promedio de Venta",
            "value": f"Bs {float(promedio):,.2f}",
            "icon":  "fa-receipt",
            "tone":  "olive",
        },
        {
            "label": "Categoría Top",
            "value": top_categoria,
            "icon":  "fa-star",
            "tone":  "caramel",
        },
    ]


def _group_sum_chart(q, col, label, chart_type="bar"):
    rows = (
        q.with_entities(col, func.sum(Venta.total_venta).label("s"))
        .group_by(col)
        .order_by(func.sum(Venta.total_venta).desc())
        .all()
    )
    return {
        "label": label,
        "type":  chart_type,
        "labels": [r[0] for r in rows],
        "data":   [float(r[1]) for r in rows],
    }


def _monthly_chart(q):
    rows = (
        q.with_entities(
            extract("month", Venta.fecha).label("m"),
            func.sum(Venta.total_venta).label("s"),
        )
        .group_by("m")
        .order_by("m")
        .all()
    )
    month_names = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    return {
        "label":  "Ventas por Mes",
        "type":   "line",
        "labels": [month_names[int(r[0]) - 1] for r in rows],
        "data":   [float(r[1]) for r in rows],
    }


def _summary_table(q):
    cols   = [Venta.sucursal, Venta.ciudad, Venta.categoria]
    labels = ["Sucursal", "Ciudad", "Categoría"]

    rows = (
        q.with_entities(
            *cols,
            func.sum(Venta.total_venta).label("total"),
            func.sum(Venta.cantidad).label("cantidad"),
            func.avg(Venta.total_venta).label("promedio"),
        )
        .group_by(*cols)
        .order_by(func.sum(Venta.total_venta).desc())
        .limit(50)
        .all()
    )

    return {
        "headers": labels + ["Total Venta (Bs)", "Cantidad", "Promedio (Bs)"],
        "rows": [
            list(r[:3]) + [f"{float(r.total):,.2f}", int(r.cantidad), f"{float(r.promedio):,.2f}"]
            for r in rows
        ],
    }


def _filter_options():
    """Devuelve las listas de valores únicos para los selectores de filtro."""
    sucursales  = [r[0] for r in db.session.query(Venta.sucursal).distinct().order_by(Venta.sucursal).all()]
    ciudades    = [r[0] for r in db.session.query(Venta.ciudad).distinct().order_by(Venta.ciudad).all()]
    categorias  = [r[0] for r in db.session.query(Venta.categoria).distinct().order_by(Venta.categoria).all()]
    metodos     = [r[0] for r in db.session.query(Venta.metodo_pago).distinct().order_by(Venta.metodo_pago).all()]
    anios       = [r[0] for r in db.session.query(extract("year", Venta.fecha)).distinct().order_by(extract("year", Venta.fecha)).all()]
    return dict(sucursales=sucursales, ciudades=ciudades, categorias=categorias, metodos=metodos, anios=anios)


# ─────────────────────────────────────────────────────────────
# Rutas
# ─────────────────────────────────────────────────────────────

@dashboard_bp.route("/ejecutivo")
@login_required
def ejecutivo():
    q = _filtered_query(request.args)

    kpis    = _executive_kpis(q)
    charts  = [
        _group_sum_chart(q, Venta.categoria,   "Ventas por Categoría",       "bar"),
        _monthly_chart(q),
        _group_sum_chart(q, Venta.metodo_pago, "Ventas por Método de Pago",  "doughnut"),
        _group_sum_chart(q, Venta.sucursal,    "Ventas por Sucursal",        "bar"),
    ]
    table   = _summary_table(q)
    options = _filter_options()

    return render_template(
        "dashboard1.html",
        kpis=kpis,
        charts=charts,
        table=table,
        options=options,
        args=request.args,
    )


@dashboard_bp.route("/api/filtros")
@login_required
def api_filtros():
    """Endpoint JSON — devuelve opciones de filtro disponibles."""
    return jsonify(_filter_options())
