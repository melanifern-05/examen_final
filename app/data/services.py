# app/data/services.py
import pandas as pd
from app.models import Venta
from app import db

# 1. FUNCIÓN QUE BUSCA TU BLUEPRINT DE IMPORTACIÓN (routes.py de data)
def import_sales_csv(file_path):
    df = pd.read_csv(file_path)
    for _, fila in df.iterrows():
        existe = db.session.query(Venta).filter_by(id_venta=int(fila['id_venta'])).first()
        if not existe:
            nueva_venta = Venta(
                id_venta=int(fila['id_venta']),
                fecha=str(fila['fecha']),
                producto=str(fila['producto']),
                categoria=str(fila['categoria']),
                cantidad=int(fila['cantidad']),
                precio_unitario=float(fila['precio_unitario']),
                total_venta=float(fila['total_venta']),
                metodo_pago=str(fila['metodo_pago']),
                sucursal=str(fila['sucursal']),
                ciudad=str(fila['ciudad']),
                vendedor=str(fila['vendedor'])
            )
            db.session.add(nueva_venta)
    db.session.commit()
    return True

# 2. CLASE QUE BUSCA TU BLUEPRINT DEL DASHBOARD (routes.py de dashboard)
class VentasService:
    @staticmethod
    def obtener_datos_desde_db():
        registros = db.session.query(Venta).all()
        if not registros:
            return {}

        datos_lista = []
        for v in registros:
            datos_lista.append({
                'fecha': v.fecha,
                'categoria': v.categoria,
                'cantidad': v.cantidad,
                'total_venta': v.total_venta,
                'sucursal': v.sucursal,
                'metodo_pago': v.metodo_pago
            })
        
        df = pd.DataFrame(datos_lista)
        
        total_ventas = round(df['total_venta'].sum(), 2)
        total_productos = int(df['cantidad'].sum())
        promedio_venta = round(df['total_venta'].mean(), 2)
        top_categoria = df.groupby('categoria')['total_venta'].sum().idxmax()
        
        ventas_cat = df.groupby('categoria')['total_venta'].sum().reset_index()
        ventas_tiempo = df.groupby('fecha')['total_venta'].sum().reset_index().tail(10)
        ventas_suc = df.groupby('sucursal')['total_venta'].sum().reset_index()
        ventas_pago = df.groupby('metodo_pago')['total_venta'].sum().reset_index()
        
        return {
            "total_ventas": total_ventas,
            "total_productos": total_productos,
            "promedio_venta": promedio_venta,
            "top_categoria": top_categoria,
            "labels_cat": ventas_cat['categoria'].tolist(),
            "values_cat": ventas_cat['total_venta'].round(2).tolist(),
            "labels_tiempo": ventas_tiempo['fecha'].tolist(),
            "values_tiempo": ventas_tiempo['total_venta'].round(2).tolist(),
            "labels_suc": ventas_suc['sucursal'].tolist(),
            "values_suc": ventas_suc['total_venta'].round(2).tolist(),
            "labels_pago": ventas_pago['metodo_pago'].tolist(),
            "values_pago": ventas_pago['total_venta'].round(2).tolist()
        }