# Usar imagen base de Python 3.11
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements.txt e instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos necesarios
COPY backend/main.py .
COPY backend/firebase-cred.json .
COPY backend/routes/ ./routes/
COPY backend/config/ ./config/

# Verificar que main.py existe
RUN ls -la /app && test -f /app/main.py || (echo "Error: main.py not found" && exit 1)

# Configurar variables de entorno
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-cred.json
ENV PYTHONPATH=/app

# Ejecutar Gunicorn con logging detallado
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "300", "--log-level", "debug", "--access-logfile", "-", "--error-logfile", "-", "main:app"]