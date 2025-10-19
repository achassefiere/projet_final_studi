# Utiliser une image Python légère
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installer les dépendances système nécessaires pour psycopg2 et Django
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de l'application
WORKDIR /app

# Copier les fichiers requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copier tout le projet
COPY . .

# Exposer le port 8000 (Django)
EXPOSE 8000

# Lancer Django avec Gunicorn
CMD ["gunicorn", "projet_studi.wsgi:application", "--bind", "0.0.0.0:8000"]