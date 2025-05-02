FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-cred.json
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "90", "main:app"]