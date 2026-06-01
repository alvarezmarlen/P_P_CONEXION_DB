from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity 
from app.extensions import db
from app.models import Categoria, Producto, Usuario


# Creamos el Blueprint para agrupar las rutas de la API bajo el prefijo /api
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- 2.1: GET /api/categorias ---
@api_bp.route('/categorias', methods=['GET'])
def get_categorias():
    """Devuelve el listado de todas las categorías para el mosaico de la Home"""
    categorias = Categoria.query.all()
    
    # Formateamos los datos a un diccionario JSON
    lista_categorias = []
    for cat in categorias:
        lista_categorias.append({
            "id": cat.id,
            "nombre": cat.nombre,
            "imagen": cat.imagen
        })
    
    return jsonify(lista_categorias), 200


# --- 2.2: GET /api/productos (Con filtros de búsqueda y categoría) ---
@api_bp.route('/productos', methods=['GET'])
def get_productos():
    """Devuelve el catálogo de productos con filtros opcionales (?categoria=X&buscar=Y)"""
    # 1. Recogemos los parámetros que vengan en la URL si los hay
    categoria_id = request.args.get('categoria', type=int)
    buscar_texto = request.args.get('buscar', type=str)
    
    # 2. Empezamos con una consulta base de todos los productos
    query = Producto.query
    
    # 3. Si piden una categoría específica, filtramos por ella
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)
        
    # 4. Si escriben algo en el buscador, filtramos por nombre (sin importar mayúsculas)
    if buscar_texto:
        query = query.filter(Producto.nombre.ilike(f"%{buscar_texto}%"))
        
    # 5. Ejecutamos la consulta final
    productos = query.all()
    
    # 6. Formateamos el resultado
    lista_productos = []
    for prod in productos:
        lista_productos.append({
            "id": prod.id,
            "nombre": prod.nombre,
            "descripcion": prod.descripcion,
            "precio": float(prod.precio), # Convertimos el Decimal a float para JSON
            "imagen": prod.imagen,
            "stock": prod.stock,
            "categoria_id": prod.categoria_id
        })
        
    return jsonify(lista_productos), 200


# --- 2.3: GET /api/productos/<id> (Detalle de un solo producto) ---
@api_bp.route('/productos/<int:producto_id>', methods=['GET'])
def get_producto_detalle(producto_id):
    """Devuelve los detalles de un único producto buscando por su ID"""
    # Buscamos el producto en la base de datos; si no existe, devuelve un error 404
    prod = Producto.query.get_or_404(producto_id)
    
    # Formateamos los datos del producto
    detalle = {
        "id": prod.id,
        "nombre": prod.nombre,
        "descripcion": prod.descripcion,
        "precio": float(prod.precio),
        "imagen": prod.imagen,
        "materiales": prod.materiales,  # Añadimos los materiales para la vista de detalle
        "stock": prod.stock,
        "categoria_id": prod.categoria_id,
        "slug": prod.slug
    }
    
    return jsonify(detalle), 200



# ==========================================
# 🔐 NUEVOS ENDPOINTS DE LA FASE 3 (ABAJO DEL TODO)
# ==========================================

# --- 3.1: POST /api/auth/register (Registro de Usuarios) ---
@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Registra un nuevo usuario en la base de datos"""
    datos = request.get_json()
    
    if not datos or not datos.get('nombre') or not datos.get('email') or not datos.get('password'):
        return jsonify({"message": "Faltan campos obligatorios (nombre, email, password)"}), 400
        
    if Usuario.query.filter_by(email=datos['email']).first():
        return jsonify({"message": "Este correo electrónico ya está registrado"}), 400
        
    nuevo_usuario = Usuario(
        nombre=datos['nombre'],
        email=datos['email']
    )
    nuevo_usuario.set_password(datos['password'])
    
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    return jsonify({"message": "Usuario registrado con éxito"}), 201


# --- 3.2: POST /api/auth/login (Inicio de sesión y entrega de Token) ---
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Verifica las credenciales y devuelve un token JWT único"""
    datos = request.get_json()
    
    if not datos or not datos.get('email') or not datos.get('password'):
        return jsonify({"message": "Faltan el email o la contraseña"}), 400
        
    usuario = Usuario.query.filter_by(email=datos['email']).first()
    
    if not usuario or not usuario.check_password(datos['password']):
        return jsonify({"message": "Credenciales incorrectas"}), 401
        
    token_acceso = create_access_token(identity=str(usuario.id))
    
    return jsonify({
        "message": "Inicio de sesión correcto",
        "token": token_acceso,
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email
        }
    }), 200
    
    
    
    # --- 3.3 y 3.4: GET /api/auth/me (Perfil del usuario protegido con JWT) ---
@api_bp.route('/auth/me', methods=['GET'])
@jwt_required()  # ← Este es el middleware que protege la ruta (Punto 3.4)
def get_perfil():
    """Devuelve los datos del usuario dueño del token actual"""
    # Recuperamos el ID del usuario que guardamos dentro del token al hacer login
    usuario_id = get_jwt_identity()
    
    # Buscamos al usuario en la base de datos
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"message": "Usuario no encontrado"}), 404
        
    return jsonify({
        "id": usuario.id,
        "nombre": usuario.nombre,
        "email": usuario.email,
        "fecha_registro": usuario.fecha_registro
    }), 200


# --- 3.6: POST /api/auth/logout (Cerrar sesión) ---
@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Cierra la sesión del usuario (en un sistema básico destruye el token en el cliente)"""
    # Como el JWT se guarda en el Frontend (Local固定Storage), cerrar sesión 
    # significa decirle al Frontend que borre el token.
    return jsonify({"message": "Sesión cerrada con éxito. Borra el token del cliente."}), 200