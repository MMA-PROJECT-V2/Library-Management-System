# 📚 Library Management System — Books Service

## 🧩 Vue d’ensemble

Le **Books Service** est un microservice du **système de gestion de bibliothèque centralisé**. Il est responsable de la gestion complète des livres : création, consultation, mise à jour, suppression (CRUD), disponibilité, statistiques et (optionnellement) les avis des utilisateurs.

Ce service est conçu pour fonctionner dans une **architecture microservices**, avec authentification et autorisation déléguées au **User Service** via JWT.

---

## 🎯 Objectifs

- Centraliser la gestion des livres
- Garantir la cohérence des données (ISBN unique, copies disponibles)
- Sécuriser les opérations sensibles par rôles
- Offrir des endpoints clairs et paginés pour le frontend

---

## ⚙️ Stack technique

- **Backend** : Django / Django REST Framework
- **Base de données** : MySQL
- **Authentification** : JWT (via User Service)
- **Tests** : Pytest
- **Documentation API** : Swagger / Redoc

---

## ⚡ Fonctionnalités

### 📘 Gestion des livres

- Création, lecture, mise à jour et suppression (CRUD)
- Pagination des résultats
- Validation de l’ISBN (unique)
- Gestion du nombre total et disponible de copies
- Calcul automatique de la disponibilité

### ⭐ Avis sur les livres (optionnel)

- Ajout d’avis (note + commentaire)
- Calcul de la note moyenne

### 📊 Statistiques

- Nombre d’emprunts
- Copies disponibles
- Fréquence d’emprunt

### 🔐 Sécurité & Middleware

- Validation du JWT via **User Service**
- Vérification des rôles (ADMIN / LIBRARIAN / USER)
- Configuration CORS

---

## 🛠️ Installation & Configuration

### 1️⃣ Cloner le projet

```bash
git clone https://github.com/MMA-PROJECT-V2/Library-Management-System.git
cd Library-Management-System/backend
git checkout feature/books-service
```

### 2️⃣ Créer un environnement virtuel

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Configuration de la base de données MySQL

Créer une base de données :

```sql
CREATE DATABASE books_db;
```

Modifier `books_service/settings.py` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'books_db',
        'USER': 'root',
        'PASSWORD': 'ton_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5️⃣ Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6️⃣ Lancer le serveur

```bash
python manage.py runserver 8002
```

---

## 🧪 Tests

### Types de tests

- Tests unitaires CRUD
- Tests des permissions par rôle
- Tests de validation des données

### Lancer les tests

```bash
pytest --cov=books_service
```

---

## 📝 Endpoints API

| Méthode | Endpoint           | Description                    | Rôle requis       |
| ------- | ------------------ | ------------------------------ | ----------------- |
| POST    | `/api/books/`      | Ajouter un livre               | LIBRARIAN / ADMIN |
| GET     | `/api/books/`      | Lister les livres (pagination) | PUBLIC            |
| GET     | `/api/books/{id}/` | Détails d’un livre             | PUBLIC            |
| PUT     | `/api/books/{id}/` | Modifier un livre              | LIBRARIAN / ADMIN |
| DELETE  | `/api/books/{id}/` | Supprimer un livre             | ADMIN             |

---

## 🔐 Sécurité

- **JWT** : tous les endpoints sécurisés nécessitent un token valide
- **Rôles** : contrôle strict des permissions
- **Principe du moindre privilège** appliqué

---

## 📦 Modèles

### 📘 Book

- `isbn` : string (unique)
- `title` : string
- `author` : string
- `publisher` : string
- `publication_year` : int
- `category` : string (FICTION, NON_FICTION, SCIENCE, ...)
- `description` : text
- `cover_image_url` : string (URL)
- `language` : string
- `pages` : int
- `total_copies` : int
- `available_copies` : int
- `times_borrowed` : int
- `average_rating` : decimal
- `is_available` : bool

### ⭐ BookReview (optionnel)

- `book_id` : int
- `user_id` : int
- `rating` : int (1–5)
- `comment` : text
- `created_at` : datetime

---

## 🌐 CORS

Configuré pour autoriser le frontend :

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
```

---

## 📚 Documentation API

- **Swagger / Redoc** (optionnel)
- Exemple :

```
http://127.0.0.1:8002/swagger/
```

---

## 🤝 Contributions

- Branche principale : `develop`
- Nouvelle fonctionnalité : `feature/<nom-feature>`
- Commits clairs, courts et descriptifs
- Pull Request obligatoire avant merge

---

## 🚀 Déploiement (aperçu)

- Conteneurisation possible avec Docker
- Intégration avec Traefik / Consul
- Variables sensibles via `.env`

---

## 📝 Auteur

**Houssem Keddam**
4ème année — Ingénierie Informatique
Projet académique : _Library Management System_

---

📌 _Ce microservice est conçu pour être évolutif, sécurisé et facilement intégrable dans un écosystème microservices._
