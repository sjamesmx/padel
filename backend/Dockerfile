FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
COPY firebase-cred.json /app/firebase-cred.json
ENV PORT=8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "90", "main:app"]