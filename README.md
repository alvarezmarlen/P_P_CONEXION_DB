# Store Sumi.chh — Backend API

API REST construida con Flask que gestiona un catálogo de bisutería artesanal, autenticación de usuarios, carrito de compras, pedidos y un panel de administración completo.

## Tecnologías utilizadas

| Tecnología | Propósito |
|---|---|
| **Python 3.11 + Flask** | Framework backend |
| **PostgreSQL** | Base de datos relacional |
| **SQLAlchemy** | ORM y modelo de datos |
| **Flask-Migrate (Alembic)** | Migraciones de base de datos |
| **Flask-JWT-Extended** | Autenticación mediante tokens JWT |
| **Werkzeug** | Hashing y verificación de contraseñas |
| **Flask-CORS** | Comunicación con el frontend |
| **Docker + Docker Compose** | Contenedores y orquestación |
| **pgAdmin** | Administración visual de la base de datos |
| **Asistente IA** | opencode/big-pickle — generación y revisión de código |

## Autor

**Marlen Alvarez** — [https://github.com/alvarezmarlen](https://github.com/alvarezmarlen)

## Estructura del proyecto

```
conexion_bd/
├── app/
│   ├── __init__.py          # Factoría de la aplicación Flask
│   ├── config.py            # Configuración por entorno (desarrollo/producción)
│   ├── extensions.py        # Instancias de db, migrate
│   ├── models.py            # Modelos SQLAlchemy (6 tablas)
│   ├── routes.py            # Todos los endpoints de la API
│   ├── seed.py              # Poblado inicial de la base de datos
│   └── static/uploads/      # Imágenes subidas desde el panel admin
├── .env.example             # Plantilla de variables de entorno
├── docker-compose.yml       # Servicios: PostgreSQL + Backend + pgAdmin
├── Dockerfile               # Construcción de la imagen del backend
├── requirements.txt         # Dependencias Python
├── run.py                   # Punto de entrada
└── db.json                  # Datos semilla (categorías y productos)
```

## Requisitos

- **Docker** + **Docker Compose** instalados

## Cómo levantar el proyecto

```bash
# 1. Clonar el repositorio
git clone https://github.com/alvarezmarlen/store-sumi.git
cd store-sumi/conexion_bd

# 2. Crear archivo .env (opcional, los valores por defecto funcionan para desarrollo)
cp .env.example .env

# 3. Iniciar los contenedores
docker compose up -d

# 4. Poblar la base de datos con datos de ejemplo
docker exec -it mi_backend flask seed-db

# 5. La API queda disponible en
#    Backend → http://localhost:{puerto_del_backend}
#    pgAdmin → http://localhost:{puerto_de_pgadmin}
```

> **Nota:** El primer usuario registrado a través de la API se convierte automáticamente en administrador.

## Endpoints de la API

### Públicos

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| `GET` | `/api/categorias` | Lista todas las categorías | — |
| `GET` | `/api/productos` | Lista productos (`?categoria=X&buscar=Y`) | — |
| `GET` | `/api/productos/<id>` | Detalle de un producto | — |
| `POST` | `/api/auth/register` | Registrar nuevo usuario | — |
| `POST` | `/api/auth/login` | Iniciar sesión (devuelve JWT) | — |
| `POST` | `/api/contacto` | Enviar mensaje de contacto | — |
| `GET` | `/api/health` | Health check del servidor | — |

### Requieren JWT

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/auth/me` | Perfil del usuario autenticado |
| `GET` | `/api/carrito` | Carrito del usuario |
| `POST` | `/api/carrito` | Añadir producto al carrito |
| `PUT` | `/api/carrito/<id>` | Actualizar cantidad |
| `DELETE` | `/api/carrito/<id>` | Eliminar ítem del carrito |
| `POST` | `/api/pedidos` | Crear pedido (checkout) |
| `GET` | `/api/pedidos` | Historial de pedidos del usuario |

### Administración (requieren JWT + is_admin)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/admin/productos` | Listar productos |
| `POST` | `/api/admin/productos` | Crear producto |
| `PUT` | `/api/admin/productos/<id>` | Editar producto |
| `DELETE` | `/api/admin/productos/<id>` | Eliminar producto |
| `GET` | `/api/admin/categorias` | Listar categorías |
| `POST` | `/api/admin/categorias` | Crear categoría |
| `PUT` | `/api/admin/categorias/<id>` | Editar categoría |
| `DELETE` | `/api/admin/categorias/<id>` | Eliminar categoría |
| `GET` | `/api/admin/usuarios` | Listar usuarios |
| `POST` | `/api/admin/usuarios` | Crear usuario |
| `PUT` | `/api/admin/usuarios/<id>` | Editar usuario |
| `PUT` | `/api/admin/usuarios/<id>/password` | Resetear contraseña |
| `DELETE` | `/api/admin/usuarios/<id>` | Eliminar usuario |
| `GET` | `/api/admin/pedidos` | Listar todos los pedidos |
| `POST` | `/api/admin/upload` | Subir imagen |

## Panel de administración

El panel permite gestionar:

- **Productos**: CRUD completo con subida de imágenes
- **Categorías**: CRUD completo
- **Usuarios**: CRUD completo con asignación de roles, reseteo de contraseñas y protección contra auto-eliminación
- **Pedidos**: Visualización de todas las órdenes con detalle de artículos

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `POSTGRES_USER` | Usuario de PostgreSQL | `usuario` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `usuario1234` |
| `POSTGRES_DB` | Nombre de la base de datos | `bd_flask` |
| `PGADMIN_EMAIL` | Email de acceso a pgAdmin | `admin@admin.com` |
| `PGADMIN_PASSWORD` | Contraseña de pgAdmin | `admin` |
| `DATABASE_URL` | URL de conexión a la base de datos | `postgresql://usuario:usuario1234@db:5432/bd_flask` |
| `JWT_SECRET_KEY` | Clave secreta para firmar los tokens JWT | `dev-insecure-change-in-prod` |
| `SECRET_KEY` | Clave secreta de Flask | — |

## Producción (Render)

Antes de desplegar en producción:

1. Configurar las variables de entorno en el panel de Render (no usar `.env`)
2. Cambiar `JWT_SECRET_KEY` por una clave segura
3. Asegurar que `DATABASE_URL` apunte a la base de datos en la nube
4. Montar un volumen persistente para `app/static/uploads/`
5. En el frontend, cambiar `API_BASE` en `assets/js/modules/api.js` a la URL de Render
