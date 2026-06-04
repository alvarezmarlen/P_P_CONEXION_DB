from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity 
from app.extensions import db
from app.models import Categoria, Producto, Usuario, Carrito, Pedido, DetallePedido, Contacto


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




# ==========================================
# 🛒 NUEVOS ENDPOINTS DE LA FASE 4 (CARRITO Y PEDIDOS)
# ==========================================

# --- 4.1.1: GET /api/carrito (Obtener el carrito del usuario) ---
@api_bp.route('/carrito', methods=['GET'])
@jwt_required()
def get_carrito():
    usuario_id = get_jwt_identity()
    items = Carrito.query.filter_by(usuario_id=usuario_id).all()
    
    resultado = []
    for item in items:
        resultado.append({
            "id": item.id,
            "producto_id": item.producto_id,
            "nombre": item.producto.nombre,
            "precio": float(item.producto.precio),
            "imagen": item.producto.imagen,
            "cantidad": item.cantidad,
            "subtotal": float(item.producto.precio) * item.cantidad
        })
    return jsonify(resultado), 200


# --- 4.1.2: POST /api/carrito (Añadir producto al carrito) ---
@api_bp.route('/carrito', methods=['POST'])
@jwt_required()
def agregar_al_carrito():
    usuario_id = get_jwt_identity()
    datos = request.get_json()
    
    producto_id = datos.get('producto_id')
    cantidad = datos.get('cantidad', 1)
    
    if not producto_id:
        return jsonify({"message": "Falta el producto_id"}), 400
        
    prod = Producto.query.get(producto_id)
    if not prod:
        return jsonify({"message": "Producto no encontrado"}), 404

    if prod.stock < cantidad:
        return jsonify({"message": f"No hay suficiente stock de: {prod.nombre}"}), 400
        
    item_existente = Carrito.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
    if item_existente:
        item_existente.cantidad += cantidad
    else:
        nuevo_item = Carrito(usuario_id=usuario_id, producto_id=producto_id, cantidad=cantidad)
        db.session.add(nuevo_item)
        
    db.session.commit()
    return jsonify({"message": "Producto añadido al carrito correctamente"}), 200


# --- 4.1.3: PUT /api/carrito/<int:item_id> (Actualizar cantidad) ---
@api_bp.route('/carrito/<int:item_id>', methods=['PUT'])
@jwt_required()
def actualizar_cantidad_carrito(item_id):
    usuario_id = get_jwt_identity()
    datos = request.get_json()
    nueva_cantidad = datos.get('cantidad')
    
    if not nueva_cantidad or nueva_cantidad <= 0:
        return jsonify({"message": "Cantidad no válida"}), 400
        
    item = Carrito.query.filter_by(id=item_id, usuario_id=usuario_id).first_or_404()
    item.cantidad = nueva_cantidad
    db.session.commit()
    
    return jsonify({"message": "Cantidad actualizada"}), 200


# --- 4.1.4: DELETE /api/carrito/<int:item_id> (Eliminar un ítem del carrito) ---
@api_bp.route('/carrito/<int:item_id>', methods=['DELETE'])
@jwt_required()
def eliminar_del_carrito(item_id):
    usuario_id = get_jwt_identity()
    item = Carrito.query.filter_by(id=item_id, usuario_id=usuario_id).first_or_404()
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Producto eliminado del carrito"}), 200


# --- 4.2: POST /api/pedidos (Crear pedido desde el carrito / Checkout) ---
@api_bp.route('/pedidos', methods=['POST'])
@jwt_required()
def crear_pedido():
    usuario_id = get_jwt_identity()
    datos = request.get_json()
    
    direccion = datos.get('direccion_envio')
    if not direccion:
        return jsonify({"message": "Falta la dirección de envío"}), 400
        
    items_carrito = Carrito.query.filter_by(usuario_id=usuario_id).all()
    if not items_carrito:
        return jsonify({"message": "El carrito está vacío. No puedes crear un pedido."}), 400
        
    total_pedido = 0
    for item in items_carrito:
        if item.producto.stock < item.cantidad:
            return jsonify({"message": f"No hay suficiente stock de: {item.producto.nombre}"}), 400
        total_pedido += float(item.producto.precio) * item.cantidad

    nuevo_pedido = Pedido(
        usuario_id=usuario_id,
        total=total_pedido,
        direccion_envio=direccion
    )
    db.session.add(nuevo_pedido)
    db.session.flush() 
    
    for item in items_carrito:
        nuevo_detalle = DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio
        )
        db.session.add(nuevo_detalle)
        
        item.producto.stock -= item.cantidad
        db.session.delete(item)
        
    db.session.commit()
    
    return jsonify({
        "message": "Pedido procesado con éxito",
        "pedido_id": nuevo_pedido.id,
        "total": total_pedido
    }), 201


# --- 4.3: GET /api/pedidos (Ver historial de compras del usuario) ---
@api_bp.route('/pedidos', methods=['GET'])
@jwt_required()
def get_historial_pedidos():
    usuario_id = get_jwt_identity()
    pedidos = Pedido.query.filter_by(usuario_id=usuario_id).order_by(Pedido.fecha.desc()).all()
    
    resultado = []
    for ped in pedidos:
        detalles_lista = []
        for det in ped.detalles:
            detalles_lista.append({
                "producto_id": det.producto_id,
                "nombre": det.producto.nombre,
                "cantidad": det.cantidad,
                "precio_unitario": float(det.precio_unitario)
            })
            
        resultado.append({
            "id": ped.id,
            "fecha": ped.fecha,
            "total": float(ped.total),
            "direccion_envio": ped.direccion_envio,
            "articulos": detalles_lista
        })
        
    return jsonify(resultado), 200




# ==========================================
# ✉️ FASE 5: FORMULARIO DE CONTACTO
# ==========================================

@api_bp.route('/contacto', methods=['POST'])
def enviar_contacto():
    datos = request.get_json()
    
    nombre = datos.get('nombre')
    email = datos.get('email')
    mensaje = datos.get('mensaje')
    
    # Validamos que el cliente no envíe campos vacíos
    if not nombre or not email or not mensaje:
        return jsonify({"message": "Todos los campos son obligatorios (nombre, email, mensaje)"}), 400
        
    # Guardamos el mensaje en la base de datos
    nuevo_mensaje = Contacto(
        nombre=nombre,
        email=email,
        mensaje=mensaje
    )
    
    db.session.add(nuevo_mensaje)
    db.session.commit()
    
    return jsonify({"message": "Mensaje de contacto enviado con éxito"}), 201