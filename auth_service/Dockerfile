# Imagen ligera de Python
FROM python:3.9-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos las dependencias e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto estándar de Flask
EXPOSE 5000

# Comando para iniciar la app escuchando en todas las interfaces (0.0.0.0)
CMD ["python", "app.py"]