import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión para continuar."
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(__name__)
    from .config import Config
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # ── Blueprints ──────────────────────────────────────────────
    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp
    from .data.routes import data_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(data_bp, url_prefix="/data")

    # ── CLI commands ────────────────────────────────────────────
    @app.cli.command("create-admin")
    @click.option("--username", default="admin")
    @click.option("--password", default="123456")
    def create_admin(username, password):
        """Crea el usuario administrador."""
        from werkzeug.security import generate_password_hash
        with app.app_context():
            existing = Usuario.query.filter_by(username=username).first()
            if existing:
                click.echo(f"Usuario '{username}' ya existe.")
                return
            u = Usuario(
                username=username,
                password=generate_password_hash(password),
                role="admin",
            )
            db.session.add(u)
            db.session.commit()
            click.echo(f"Admin '{username}' creado con password '{password}'.")

    @app.cli.command("import-csv")
    @click.option("--path", default="ventas_supermercado.csv")
    def import_csv(path):
        """Importa el CSV de ventas a la base de datos."""
        from .data.services import import_sales_csv
        with app.app_context():
            result = import_sales_csv(path)
            click.echo(result)

    return app


# PASOS PARA EJECUTAR:
# 1. pip install -r requirements.txt
# 2. flask db init
# 3. flask db migrate -m "initial"
# 4. flask db upgrade
# 5. flask create-admin
# 6. flask import-csv --path ventas_supermercado.csv
# 7. flask run
# Login: admin / 123456
