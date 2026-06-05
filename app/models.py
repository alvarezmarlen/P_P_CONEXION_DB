from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    
    # Relación inversa: una categoría tiene muchos productos
    productos = db.relationship('Producto', backref='categoria', lazy=True)


class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    imagen = db.Column(db.String(255), nullable=True)
    materiales = db.Column(db.String(255), nullable=True)
    stock = db.Column(db.Integer, default=0, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    total = db.Column(db.Numeric(10, 2), nullable=False)
    direccion_envio = db.Column(db.String(255), nullable=False)
    
    # Relación para acceder a los detalles de este pedido
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)


class DetallePedido(db.Model):
    __tablename__ = 'detalles_pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    
    producto = db.relationship('Producto')


class Carrito(db.Model):
    __tablename__ = 'carrito'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    
    producto = db.relationship('Producto', backref='en_carritos')
    usuario = db.relationship('Usuario', backref='carrito_items')


# ==========================================
# 📝 MODELO DE LA FASE 5: FORMULARIO DE CONTACTO
# ==========================================
class Contacto(db.Model):
    __tablename__ = 'contactos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())