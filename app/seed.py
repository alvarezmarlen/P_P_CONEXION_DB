import os
import json
from app.extensions import db
from app.models import Categoria, Producto

def seed_database():
    # Buscamos el archivo db.json en la raíz del proyecto
    json_path = os.path.join(os.getcwd(), 'db.json')
    
    if not os.path.exists(json_path):
        print(f"❌ Error: No se encuentra el archivo db.json en {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    productos_json = data.get('productos', [])
    print(f"📦 Leyendo {len(productos_json)} productos del archivo db.json...")

    # Diccionario auxiliar para guardar las categorías que vamos creando
    categorias_creadas = {}

    for prod in productos_json:
        nombre_cat = prod.get('categoria')
        
        # 1. Si la categoría no está en la base de datos, la creamos
        if nombre_cat not in categorias_creadas:
            categoria_obj = Categoria.query.filter_by(nombre=nombre_cat).first()
            if not categoria_obj:
                categoria_obj = Categoria(
                    nombre=nombre_cat,
                    imagen=None # Puedes meterle una por defecto si quieres
                )
                db.session.add(categoria_obj)
                db.session.flush() # Esto nos da el ID de la categoría de inmediato
                print(f"📁 Categoría creada: {nombre_cat}")
            categorias_creadas[nombre_cat] = categoria_obj
        
        # 2. Comprobamos si el producto ya existe mediante el slug
        slug_prod = prod.get('slug')
        producto_existente = Producto.query.filter_by(slug=slug_prod).first()
        
        if not producto_existente:
            nuevo_producto = Producto(
                slug=slug_prod,
                categoria_id=categorias_creadas[nombre_cat].id,
                nombre=prod.get('productName'), # Usamos productName de tu json
                descripcion=prod.get('descripcion'),
                precio=prod.get('precio'),
                imagen=prod.get('imagen'),
                materiales=prod.get('materiales'),
                stock=prod.get('stock', 0)
            )
            db.session.add(nuevo_producto)
            print(f"   ✅ Producto preparado: {prod.get('productName')}")

    # Guardamos definitivamente todos los cambios en PostgreSQL
    try:
        db.session.commit()
        print("🚀 ¡Base de datos rellenada con éxito en PostgreSQL!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al guardar en la base de datos: {e}")