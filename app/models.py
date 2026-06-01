from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        """Transforma la contraseña de texto plano en un hash ilegible"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Compara la contraseña introducida con el hash guardado"""
        return check_password_hash(self.password_hash, password)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)


class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    imagen = db.Column(db.String(255), nullable=True)
    
    # Relación con Producto
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    materiales = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, default=0)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    direccion_envio = db.Column(db.String(255), nullable=False)
    
    # Relación con Detalles
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)

class DetallePedido(db.Model):
    __tablename__ = 'detalles_pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)