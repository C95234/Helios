FROM python:3.12-slim

WORKDIR /app

# Dependances d'abord (couche mise en cache separement du code applicatif).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# app/data/*.json (adjacence des departements, batterie INSEE) est deja dans
# le repo -- pre-calcule par scripts/, jamais recalcule au demarrage du conteneur.

EXPOSE 8000

ENV HELIOS_ENV=production

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
