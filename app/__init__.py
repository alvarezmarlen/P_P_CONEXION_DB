from flask import Flask, jsonify
from flask_cors import CORS
from app.config import config_options
from app.extensions import db, migrate

def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)


# LE DECIMOS A FLASK QUE CARGUE LAS CONFIGURACIONES:
    app.config.from_object(config_options[config_name])
    
    db.init_app(app)                          # ← init dentro de la función

# ¡IMPORTANTE!: Importamos los modelos para que Flask-Migrate los "vea"
    from app import models    
    migrate.init_app(app, db)

# 👇 LÍNEAS AQUÍ ABAJO PARA EL COMANDO SEED:
    from app.seed import seed_database
    @app.cli.command("seed-db")
    def seed_db_command():
        """Rellena la base de datos con los datos de db.json"""
        seed_database()
    
    # Aquí puedes registrar tus rutas o inicializar tu Base de Datos más adelante
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Backend funcionando"})

# 🔗 REGISTRAMOS EL NUEVO ARCHIVO DE RUTAS AQUÍ:
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    
    return app
