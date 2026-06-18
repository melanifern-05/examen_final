# app/models.py
from app import db
from datetime import datetime

class Venta(db.Model):
    __tablename__ = 'ventas'
    id_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(20), nullable=False)
    producto = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    total_venta = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    sucursal = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    vendedor = db.Column(db.String(100), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')

class BitacoraAcceso(db.Model):
    __tablename__ = 'bitacora_accesos'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    fecha_acceso = db.Column(db.DateTime, default=datetime.utcnow)
    accion = db.Column(db.String(100))