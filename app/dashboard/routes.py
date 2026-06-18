# app/dashboard/routes.py
from flask import Blueprint, render_template
from app.data.services import VentasService

# Instanciamos tu Blueprint del Dashboard
dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')

@dashboard_bp.route('/dashboard1')
def dashboard1():
    try:
        # Llamamos al conector de PostgreSQL en Render
        datos = VentasService.obtener_datos_desde_db()
        
        # Desempaquetamos los datos en el HTML rojo
        return render_template('dashboard1.html', **datos)
    except Exception as e:
        return f"Error de conexión con PostgreSQL Render: {str(e)}", 500