from dotenv import load_dotenv
load_dotenv()
import os

class Config:
    """Configuración base con variables que comparten todos los entornos"""
    # Clave secreta para proteger sesiones y tokens (si no existe, usa una por defecto)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'
    
    # Desactivar el rastreo de modificaciones de SQLAlchemy para ahorrar memoria
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configuración específica para tu ordenador (Modo Desarrollo)"""
    DEBUG = True
    # Aquí pones la ruta a tu base de datos local (por ejemplo, SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'

class ProductionConfig(Config):
    """Configuración específica para cuando lo subas a internet (Render)"""
    DEBUG = False
    # En producción, Render te dará la URL de la base de datos real
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Diccionario para facilitar el acceso a los diferentes entornos
config_options = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}