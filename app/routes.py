from flask import Blueprint, jsonify, request
from app.models import Categoria, Producto

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