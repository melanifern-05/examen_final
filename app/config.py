# app/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_secreta_cafe_andino'
    
    # Tu cadena de conexión real de Render PostgreSQL
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://cafe_andino:ymySVxIlZbNhCGbgCdHbLbYD8iUO0x8I@dpg-d8c26gl7vvec73b74r90-a.oregon-postgres.render.com/cafe_andino_11ey"
    SQLALCHEMY_TRACK_MODIFICATIONS = False