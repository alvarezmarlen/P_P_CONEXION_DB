from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # Esto crea las tablas y ejecuta el seed automáticamente al iniciar
    db.create_all()
    try:
        from app.seed import seed_database
        seed_database()
    except Exception as e:
        print("El seed ya se ejecutó o hubo un detalle:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)