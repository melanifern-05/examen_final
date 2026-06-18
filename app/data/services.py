import csv
from datetime import datetime
from .. import db
from ..models import Venta

EXPECTED_COLUMNS = [
    "id_venta", "fecha", "producto", "categoria", "cantidad",
    "precio_unitario", "total_venta", "metodo_pago", "sucursal",
    "ciudad", "vendedor",
]


def _row_to_sale(row):
    return Venta(
        id_venta_csv    = int(row["id_venta"]),
        fecha           = datetime.strptime(row["fecha"], "%Y-%m-%d").date(),
        producto        = row["producto"].strip(),
        categoria       = row["categoria"].strip(),
        cantidad        = int(row["cantidad"]),
        precio_unitario = float(row["precio_unitario"]),
        total_venta     = float(row["total_venta"]),
        metodo_pago     = row["metodo_pago"].strip(),
        sucursal        = row["sucursal"].strip(),
        ciudad          = row["ciudad"].strip(),
        vendedor        = row["vendedor"].strip(),
    )


def import_sales_csv(path: str) -> str:
    try:
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            # Validar columnas
            missing = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
            if missing:
                return f"ERROR: columnas faltantes en CSV: {missing}"

            inserted = skipped = errors = 0
            for row in reader:
                try:
                    id_csv = int(row["id_venta"])
                    if Venta.query.filter_by(id_venta_csv=id_csv).first():
                        skipped += 1
                        continue
                    sale = _row_to_sale(row)
                    db.session.add(sale)
                    inserted += 1
                except Exception as e:
                    errors += 1
                    print(f"  Fila {row.get('id_venta','?')} error: {e}")

            db.session.commit()
            return (
                f"Importación completa: {inserted} insertados, "
                f"{skipped} ya existían, {errors} errores."
            )
    except FileNotFoundError:
        return f"ERROR: archivo '{path}' no encontrado."
    except Exception as e:
        db.session.rollback()
        return f"ERROR inesperado: {e}"
