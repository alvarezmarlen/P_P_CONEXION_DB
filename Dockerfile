# Imagen base oficial de Python liviana
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# PRIMERO copiamos requirements.txt solo
# Así Docker usa caché y no reinstala si no cambiaron las librerías
COPY requirements.txt .

# Docker hace el pip install AQUÍ DENTRO — no en tu terminal
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copiamos el resto del código
COPY . .

# Puerto que usa Flask
EXPOSE 5000

# Comando de arranque
CMD ["python", "run.py"]