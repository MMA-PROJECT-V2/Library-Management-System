# 📚 Library Management System

<<<<<<< HEAD
> A modern microservices-based library management application built with Django and Vue.js

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=coverage)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System)

---

## 🎯 Project Overview

This project was developed as part of the **Agile Management Methods** course at the University of Boumerdès. It demonstrates the practical application of **SCRUM methodology** and **DevOps practices** in building a full-stack web application.

### Key Learning Objectives

- ✅ Apply **SCRUM** agile methodology for project management
- ✅ Utilize **GitHub** for version control and team collaboration
- ✅ Implement an effective **branching strategy**
- ✅ Integrate **SonarQube** for automated code quality analysis
- ✅ Configure **unit testing** with code coverage metrics
- ✅ Build an automated **CI/CD pipeline** using GitHub Actions

---

## 👥 Development Team

| Name | Role | Responsibilities |
|------|------|------------------|
| **Abdelhafidh** | 🎯 Scrum Master | Sprint planning, team facilitation, impediment removal |
| **Ahmed** | 💻 Backend Developer | Microservices architecture, API development |
| **Houssem** | 🎨 Frontend Developer | Vue.js UI/UX implementation |
| **Aymen** | 🧪 Tester / DevOps | Quality assurance, CI/CD pipeline setup |
| **Amine** | 📋 Product Owner | Requirements gathering, backlog prioritization |

---

## 🏗️ Architecture

Our application follows a modern microservices architecture designed for scalability and maintainability.

### Tech Stack

<table>
  <tr>
    <td align="center"><b>Frontend</b></td>
    <td>Vue.js 3</td>
  </tr>
  <tr>
    <td align="center"><b>Backend</b></td>
    <td>Django + Django REST Framework</td>
  </tr>
  <tr>
    <td align="center"><b>Database</b></td>
    <td>MySQL 5.7+</td>
  </tr>
  <tr>
    <td align="center"><b>Testing</b></td>
    <td>PyTest</td>
  </tr>
  <tr>
    <td align="center"><b>CI/CD</b></td>
    <td>GitHub Actions</td>
  </tr>
  <tr>
    <td align="center"><b>Code Quality</b></td>
    <td>SonarQube</td>
  </tr>
  <tr>
    <td align="center"><b>Project Management</b></td>
    <td>Jira Software</td>
  </tr>
</table>

### 📂 Project Structure

```
Library-Management-System/
│
├── 📁 backend/                              # Backend microservices
│   ├── 📁 api-gateway/                      # API entry point & request routing
│   ├── 📁 user-service/                     # User management microservice
│   ├── 📁 books-service/                    # Book catalog microservice
│   ├── 📁 loans-service/                    # Loan tracking microservice
│   ├── 📁 notifications-service/            # Notification system
│   └── 📁 shared/                           # Shared utilities & configurations
│
├── 📁 frontend/                             # Vue.js client application
│
├── 📁 tests/                                # Integration & E2E tests
│
├── 📁 docs/                                 # Project documentation
│
├── 📁 scripts/                              # Deployment & maintenance scripts
│
├── 📄 docker-compose.yml                    # Docker orchestration
├── 📄 .gitignore                            # Git ignore rules
├── 📄 README.md                             # This file
├── 📄 LICENSE                               # Project license
└── 📄 CONTRIBUTING.md                       # Contribution guidelines
```

---

## 📊 Code Quality Metrics

We maintain high code quality standards through continuous monitoring:

| Metric | Status |
|--------|--------|
| **Bugs** | [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=bugs)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System) |
| **Code Smells** | [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System) |
| **Technical Debt** | [![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System) |
| **Duplicated Lines** | [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System) |
| **Lines of Code** | [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System) |
| **Reliability** | [![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=MMA-PROJECT-V2_Library-Management-System&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=MMA-PROJECT-V2_Library-Management-System) |

---

## 🌿 Git Branching Strategy

We follow **Git Flow**, adapted for agile SCRUM development:

```
main
  ├── develop
  │     ├── feature/add-auth-api
  │     ├── feature/book-search
  │     └── fix/typo-in-dashboard
  └── hotfix/fix-login-crash
```

### Branch Types

| Branch | Purpose | Source | Merge Target |
|--------|---------|--------|--------------|
| `main` | 🔒 Production-ready code | - | - |
| `develop` | 🔄 Integration branch | `main` | `main` |
| `feature/*` | ✨ New features | `develop` | `develop` |
| `fix/*` | 🐛 Bug fixes | `develop` | `develop` |
| `hotfix/*` | 🚨 Critical production fixes | `main` | `main` + `develop` |

**Example branch names:**
- `feature/add-user-authentication`
- `fix/broken-search-results`
- `hotfix/database-connection-error`

---

## 🚀 CI/CD Pipeline

Our automated pipeline ensures code quality and reliability on every commit.

### Pipeline Stages

```mermaid
graph LR
    A[Push/PR] --> B[Checkout Code]
    B --> C[Install Dependencies]
    C --> D[Run Unit Tests]
    D --> E[Code Coverage]
    E --> F[SonarQube Analysis]
    F --> G{Quality Gate}
    G -->|Pass| H[✅ Success]
    G -->|Fail| I[❌ Blocked]
```

### What Happens on Each Push:

1. **🔍 Initialization** - Validate project configuration
2. **🧪 Testing** - Execute unit tests with PyTest
3. **📈 Coverage** - Calculate code coverage metrics
4. **🔎 Quality Analysis** - Analyze code with SonarQube
5. **✅ Quality Gate** - Enforce quality standards

---

## 📋 Agile Methodology

### SCRUM Implementation

- **Framework:** SCRUM
- **Tool:** Jira Software
- **Sprint Duration:** 2 weeks
- **Total Sprints:** 4
- **Initial Backlog:** 10+ user stories

### Sprint Breakdown

| Sprint | Focus |
|--------|-------|
| **Sprint 0** | Environment setup, DevOps configuration |
| **Sprint 1** | User authentication & book catalog |
| **Sprint 2** | Loan management system |
| **Sprint 3** | Notifications & reporting |
| **Sprint 4** | Testing, refinement & deployment |

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python** 3.8 or higher
- **Node.js** 14 or higher
- **MySQL** 5.7 or higher
- **Git**

### Quick Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Abdelhafidh-87/Library-management-system.git
cd Library-management-system
```

#### 2️⃣ Backend Setup

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
```

#### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run serve
```

#### 4️⃣ Database Configuration

1. Create a MySQL database
2. Copy `.env.example` to `.env`
3. Update database credentials in `.env`

```env
DB_NAME=library_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

#### 5️⃣ Run the Application

**Backend:**
```bash
python manage.py runserver
```

**Frontend:**
```bash
npm run serve
```

Visit `http://localhost:8080` to access the application! 🎉

---

## 📖 Documentation

Detailed documentation is available in the `docs/` directory:

- **Installation Guide** - Complete setup instructions
- **API Documentation** - REST API endpoints reference
- **User Manual** - Application usage guide
- **Development Guide** - Contributing guidelines

---

## 🤝 Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code of conduct
- Development workflow
- Pull request process
- Coding standards

---

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

## 📞 Contact

For questions or support, please open an issue on GitHub or contact the development team.

---

<div align="center">

**Made with ❤️ by the University of Boumerdès Development Team**

⭐ Star this repository if you find it helpful!

</div>
=======
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
>>>>>>> develop
