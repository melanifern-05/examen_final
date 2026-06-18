from datetime import datetime
from flask_login import UserMixin
from . import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role     = db.Column(db.String(20), default="viewer")
    activo   = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Usuario {self.username}>"


class BitacoraAcceso(db.Model):
    __tablename__ = "bitacora_acceso"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    evento     = db.Column(db.String(120))
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)
    ip         = db.Column(db.String(50))

    usuario = db.relationship("Usuario", backref="accesos")


class Venta(db.Model):
    __tablename__ = "ventas"
    id            = db.Column(db.Integer, primary_key=True)
    id_venta_csv  = db.Column(db.Integer, unique=True, nullable=False)
    fecha         = db.Column(db.Date, nullable=False, index=True)
    producto      = db.Column(db.String(180), nullable=False, index=True)
    categoria     = db.Column(db.String(100), nullable=False, index=True)
    cantidad      = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    total_venta   = db.Column(db.Numeric(14, 2), nullable=False, index=True)
    metodo_pago   = db.Column(db.String(80), nullable=False, index=True)
    sucursal      = db.Column(db.String(120), nullable=False, index=True)
    ciudad        = db.Column(db.String(100), nullable=False, index=True)
    vendedor      = db.Column(db.String(160), nullable=False, index=True)

    def __repr__(self):
        return f"<Venta {self.id_venta_csv} {self.producto}>"
