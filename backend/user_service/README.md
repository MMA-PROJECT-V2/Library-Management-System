# User Service - Library Management System

A microservice for user management and authentication in the Library Management System, built with Django REST Framework.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)

## 🎯 Overview

The User Service handles all user-related operations including authentication, authorization, and profile management. It provides JWT-based authentication and a flexible role-based permission system for the Library Management System.

## ✨ Features

### Authentication & Authorization

- **JWT Authentication**: Secure token-based authentication using `djangorestframework-simplejwt`
- **User Registration**: Email-based user registration with password validation
- **User Login**: Secure login with access and refresh tokens
- **Token Validation**: Endpoint for microservices to validate tokens
- **Permission Checking**: Granular permission validation for microservices

### User Management

- **User Profiles**: Extended profile information (bio, address, avatar, birth date)
- **Role-Based Access**: Three user roles (MEMBER, LIBRARIAN, ADMIN)
- **Group-Based Permissions**: Flexible permission system with custom groups
- **Direct Permissions**: Ability to assign permissions directly to users

### Permission System

- **Custom Permissions**: Library-specific permissions (can_view_books, can_borrow_book, etc.)
- **Permission Categories**: Organized by category (BOOKS, LOANS, USERS, REPORTS, SYSTEM)
- **Auto-Configuration**: Default groups and permissions created on startup
- **Hierarchical Access**: Admin users have all permissions automatically

## 🛠 Tech Stack

- **Framework**: Django 4.2.7
- **API Framework**: Django REST Framework 3.14.0
- **Authentication**: djangorestframework-simplejwt 5.5.1
- **Database**: MySQL (via mysqlclient 2.1.1)
- **Testing**: pytest 7.4.3, pytest-django 4.5.2, pytest-cov 4.1.0
- **CORS**: django-cors-headers 4.3.1
- **Configuration**: python-decouple 3.8

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip

### Installation

1. **Clone the repository**

```bash
cd backend/user_service
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the `user_service` directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=user_service_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# Service URLs (for inter-service communication)
USER_SERVICE_URL=http://localhost:8001
BOOK_SERVICE_URL=http://localhost:8002
LOAN_SERVICE_URL=http://localhost:8003
```

5. **Create database**

```bash
mysql -u root -p
CREATE DATABASE user_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

6. **Run migrations**

```bash
python manage.py migrate
```

7. **Create superuser (optional)**

```bash
python manage.py createsuperuser
```

8. **Run the development server**

```bash
python manage.py runserver 8001
```

The service will be available at `http://localhost:8001`

## 📚 API Documentation

See [API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md) for complete API reference.

### Quick Reference

#### Authentication Endpoints

- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login user
- `POST /api/users/token/` - Obtain JWT token pair
- `POST /api/users/token/refresh/` - Refresh access token

#### User Endpoints

- `GET /api/users/me/` - Get current user info
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile

#### Microservice Endpoints

- `POST /api/users/validate/` - Validate JWT token
- `POST /api/users/check-permission/` - Check user permissions

## 🧪 Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=users --cov-report=html
```

### Run specific test file

```bash
pytest users/tests/test_models.py
```

### Run specific test class

```bash
pytest users/tests/test_views_auth.py::TestRegisterView
```

### Current Test Coverage

- **Overall Coverage**: 84.36%
- **Models**: 84.03%
- **Views**: 97.44%
- **Serializers**: 98.44%

## 📁 Project Structure

```
user_service/
├── manage.py
├── pytest.ini
├── requirements.txt
├── user_service/
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── test_settings.py     # Test-specific settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
└── users/
    ├── __init__.py
    ├── models.py            # User, UserProfile, Permission, Group models
    ├── serializers.py       # DRF serializers
    ├── views.py             # API views
    ├── urls.py              # App URL patterns
    ├── admin.py
    ├── apps.py              # App configuration & auto-setup
    ├── migrations/
    └── tests/
        ├── __init__.py
        ├── conftest.py      # Pytest fixtures
        ├── test_models.py
        ├── test_serializers.py
        ├── test_views_auth.py
        └── test_views_introspection.py
```

## ⚙️ Configuration

### JWT Settings

Configure JWT tokens in `user_service/settings.py`:

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

### CORS Settings

For development, all origins are allowed:

```python
CORS_ALLOW_ALL_ORIGINS = True  # For development only
```

For production, restrict to specific origins:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]
```

### Default Roles & Permissions

The service automatically creates default groups on startup:

- **MEMBER**: Can view books, borrow/return books, view own loans
- **LIBRARIAN**: Can manage books, view all loans, manage loans
- **ADMIN**: Has all permissions

## 🔐 Security Features

- Password hashing using Django's default PBKDF2 algorithm
- JWT token-based authentication
- Token expiration and refresh mechanism
- Role-based access control (RBAC)
- Permission-based authorization
- CORS protection
- SQL injection protection (Django ORM)
- XSS protection (Django templates)

## 📊 Database Models

### User

- Email-based authentication
- Roles: MEMBER, LIBRARIAN, ADMIN
- Custom groups and permissions
- Max loans limit

### UserProfile

- Bio
- Address
- Avatar URL
- Birth date

### Permission

- Code (unique identifier)
- Name (human-readable)
- Category (BOOKS, LOANS, USERS, REPORTS, SYSTEM)
- Description

### Group

- Name
- Description
- Permissions (many-to-many)
- Is default flag

## 🤝 Integration with Other Services

This service provides token validation and permission checking endpoints for other microservices:

```python
# Example: Book Service validating a token
response = requests.post(
    "http://localhost:8001/api/users/validate/",
    json={"token": access_token}
)

if response.json()["valid"]:
    user_data = response.json()["user"]
    # Proceed with authenticated request
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check MySQL is running
sudo service mysql status

# Test connection
mysql -u root -p -e "SHOW DATABASES;"
```

### Migration Issues

```bash
# Reset migrations (development only)
python manage.py migrate users zero
python manage.py migrate
```

### Port Already in Use

```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>
```

## 📝 License

This project is part of the Library Management System microservices architecture.

## 👥 Contributors

- Development Team - Initial work

## 📞 Support

For issues and questions, please contact the development team or create an issue in the repository.
