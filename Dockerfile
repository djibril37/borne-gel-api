FROM python:3.11-slim

# Docker va créer ce dossier tout seul
WORKDIR /code

# Installer les dépendances système (On garde tes bonnes pratiques !)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# LA CLÉ DU SUCCÈS : On copie ton dossier 'app' DANS un dossier 'app'
COPY ./app ./app

# Exposer le port
EXPOSE 8000

# On lance en précisant bien le chemin complet
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]