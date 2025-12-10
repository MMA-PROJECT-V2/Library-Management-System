# Loans Service

Microservice de gestion des emprunts de livres.

## Installation
```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

## Base de données
```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

## Lancer le service
```bash
python manage.py runserver 8003
```

## Tests
```bash
pytest
```
