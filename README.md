# Library-Management-Systeme
systeme de gestion de bibliotheque centralise

# Books Service - Library Management System

## 📖 Description
Le microservice **Books Service** gère tout ce qui concerne les livres dans le système de gestion de bibliothèque.  
Il permet la création, lecture, mise à jour et suppression des livres (CRUD), ainsi que la gestion des avis sur les livres.

---

## ⚡ Fonctionnalités

- CRUD complet sur les livres :
  - **Créer un livre** (POST /books) – accessible aux rôles **LIBRARIAN/ADMIN**
  - **Lister les livres** (GET /books) avec pagination
  - **Afficher les détails d’un livre** (GET /books/{id})
  - **Modifier un livre** (PUT /books/{id}) – accessible aux rôles **LIBRARIAN/ADMIN**
  - **Supprimer un livre** (DELETE /books/{id}) – accessible uniquement au rôle **ADMIN**
- Gestion des avis sur les livres (**optionnel**)
- Vérification de la disponibilité des livres
- Statistiques : nombre d’emprunts, copies disponibles
- Validation de l’ISBN unique
- Middleware pour :
  - Vérification JWT (via User Service)
  - Vérification des rôles
- Configuration CORS

---

## 🛠️ Installation

1. **Cloner le projet**
```bash
git clone https://github.com/MMA-PROJECT-V2/Library-Management-System.git
cd Library-Management-System/backend
git checkout feature/books-service


Créer un environnement virtuel

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/macOS


Installer les dépendances

pip install -r requirements.txt


Configurer la base de données MySQL

Créer une base de données : books_db

Modifier books_service/settings.py :

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


Appliquer les migrations

python manage.py makemigrations
python manage.py migrate


Lancer le serveur

python manage.py runserver 8002

📝 Endpoints API
Méthode	Endpoint	Description	Rôle requis
POST	/api/books/	Ajouter un livre	LIBRARIAN/ADMIN
GET	/api/books/	Liste des livres (pagination)	PUBLIC
GET	/api/books/{id}/	Détails d’un livre	PUBLIC
PUT	/api/books/{id}/	Modifier un livre	LIBRARIAN/ADMIN
DELETE	/api/books/{id}/	Supprimer un livre	ADMIN
🔐 Sécurité

JWT : tous les endpoints nécessitant authentification utilisent un middleware qui valide le token via User Service.

Roles : vérification des permissions pour certaines actions (CRUD limité aux rôles LIBRARIAN/ADMIN/ADMIN).

📦 Modèles
Book

isbn : string, unique

title : string

author : string

publisher : string

publication_year : int

category : string (FICTION, NON_FICTION, SCIENCE...)

description : text

cover_image_url : string (URL)

language : string

pages : int

total_copies : int

available_copies : int

times_borrowed : int

average_rating : decimal

is_available : bool

BookReview (optionnel)

book_id : int

user_id : int

rating : int (1-5)

comment : text

created_at : datetime

🧪 Tests

Tests unitaires CRUD

Tests des permissions par rôle

Commande pour lancer les tests :

pytest --cov=books_service

🌐 CORS

Configuré pour accepter les requêtes depuis le frontend

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

📚 Documentation

Swagger / Redoc (optionnel)

Exemple : http://127.0.0.1:8002/swagger/

🔧 Contributions

Branche principale : develop

Nouvelle fonctionnalité : feature/<nom-feature>

Commits clairs et descriptifs

📝 Auteur

Projet réalisé par Houssem Keddam - 4ème année Ingénierie Informatique

Microservice Books Service


---

💡 **Conseil** : crée un fichier `README.md` dans le dossier **`backend/books_service/`**, colle ce contenu, puis commit sur ta branche `feature/books-service` :

```bash
git add README.md
git commit -m "Ajout README complet pour Books Service"
git push origin feature/books-service
