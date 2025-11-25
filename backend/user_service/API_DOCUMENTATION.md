# User Service API Documentation

Complete API reference for the User Service microservice.

## Base URL

```
http://localhost:8001/api/users
```

## Table of Contents

1. [Authentication](#authentication)
2. [User Registration (US2)](#user-registration-us2)
3. [User Login (US2)](#user-login-us2)
4. [Token Management](#token-management)
5. [User Profile (US3)](#user-profile-us3)
6. [Microservice Endpoints](#microservice-endpoints)

---

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## User Registration (US2)

### Register New User

Create a new user account.

**Endpoint:** `POST /api/users/register/`

**Authentication:** Not required

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Required Fields:**

- `email` (string, unique, valid email format)
- `username` (string, unique)
- `password` (string, minimum 8 characters)

**Optional Fields:**

- `first_name` (string)
- `last_name` (string)
- `phone` (string)

**Success Response (201 Created):**

```json
{
  "message": "Inscription réussie.",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "MEMBER",
    "is_active": true,
    "max_loans": 5,
    "date_joined": "2025-11-25T10:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**

```json
// 400 Bad Request - Duplicate email
{
  "email": ["user with this email already exists."]
}

// 400 Bad Request - Weak password
{
  "password": ["Ensure this field has at least 8 characters."]
}

// 400 Bad Request - Invalid email
{
  "email": ["Enter a valid email address."]
}
```

**Business Rules:**

- Email must be unique
- Password must be at least 8 characters
- New users are assigned MEMBER role by default
- New users are automatically added to MEMBER group
- Users are active by default
- Access and refresh tokens are returned immediately

---

## User Login (US2)

### Login User

Authenticate user and obtain JWT tokens.

**Endpoint:** `POST /api/users/login/`

**Authentication:** Not required

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**

```json
{
  "message": "Connexion réussie.",
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "MEMBER",
    "is_active": true,
    "max_loans": 5,
    "date_joined": "2025-11-25T10:30:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**

```json
// 400 Bad Request - Invalid credentials
{
  "non_field_errors": ["Email ou mot de passe incorrect."]
}

// 400 Bad Request - Inactive account
{
  "non_field_errors": ["Ce compte est désactivé."]
}
```

**Business Rules:**

- Email and password are required
- Account must be active
- Returns access token (30 min expiry) and refresh token (7 days expiry)
- Failed login attempts do not lock the account

---

## Token Management

### Obtain Token Pair

Alternative endpoint to get JWT tokens.

**Endpoint:** `POST /api/users/token/`

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Access Token

Get a new access token using refresh token.

**Endpoint:** `POST /api/users/token/refresh/`

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Notes:**

- Access token expires after 30 minutes
- Refresh token expires after 7 days
- Refresh tokens are rotated (new refresh token returned)
- Old refresh tokens are blacklisted after rotation

---

## User Profile (US3)

### Get Current User

Get authenticated user's information with permissions.

**Endpoint:** `GET /api/users/me/`

**Authentication:** Required (JWT)

**Success Response (200 OK):**

```json
{
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "MEMBER",
    "is_active": true,
    "max_loans": 5,
    "date_joined": "2025-11-25T10:30:00Z",
    "is_staff": false,
    "is_superuser": false,
    "permissions": [
      "can_view_books",
      "can_borrow_book",
      "can_return_book",
      "can_view_loans"
    ],
    "groups": ["MEMBER"]
  }
}
```

**Error Response:**

```json
// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

### Get User Profile

Get extended profile information.

**Endpoint:** `GET /api/users/profile/`

**Authentication:** Required (JWT)

**Success Response (200 OK):**

```json
{
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "MEMBER",
    "is_active": true,
    "max_loans": 5,
    "date_joined": "2025-11-25T10:30:00Z"
  },
  "bio": "Book enthusiast and avid reader",
  "address": "123 Main St, Algiers, Algeria",
  "avatar_url": "https://example.com/avatars/johndoe.jpg",
  "birth_date": "1990-05-15"
}
```

**Notes:**

- Profile is created automatically if it doesn't exist
- All profile fields are optional

### Update User Profile

Update extended profile information.

**Endpoint:** `PUT /api/users/profile/`

**Authentication:** Required (JWT)

**Request Body:**

```json
{
  "bio": "Updated bio text",
  "address": "456 New Street, Algiers",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "birth_date": "1990-05-15"
}
```

**All fields are optional (partial update supported)**

**Success Response (200 OK):**

```json
{
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "MEMBER",
    "is_active": true,
    "max_loans": 5,
    "date_joined": "2025-11-25T10:30:00Z"
  },
  "bio": "Updated bio text",
  "address": "456 New Street, Algiers",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "birth_date": "1990-05-15"
}
```

**Error Responses:**

```json
// 400 Bad Request - Invalid date
{
  "birth_date": ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]
}

// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Business Rules:**

- Users can only view and update their own profile
- All fields are optional
- Profile is created on first access if it doesn't exist

---

## Microservice Endpoints

These endpoints are used by other microservices for authentication and authorization.

### Validate Token

Validate JWT token and get user data.

**Endpoint:** `POST /api/users/validate/`

**Authentication:** Not required (called by other services)

**Request Body:**

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response (200 OK):**

```json
{
  "valid": true,
  "user": {
    "id": 1,
    "email": "john.doe@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "MEMBER",
    "is_active": true,
    "max_loans": 5,
    "date_joined": "2025-11-25T10:30:00Z",
    "is_staff": false,
    "is_superuser": false,
    "permissions": [
      "can_view_books",
      "can_borrow_book",
      "can_return_book",
      "can_view_loans"
    ],
    "groups": ["MEMBER"]
  }
}
```

**Error Responses:**

```json
// 400 Bad Request - Missing token
{
  "valid": false,
  "error": "Token is required"
}

// 401 Unauthorized - Invalid token
{
  "valid": false,
  "error": "Invalid token: Token is invalid or expired"
}

// 401 Unauthorized - Inactive user
{
  "valid": false,
  "error": "User account is disabled"
}
```

### Check Permission

Check if user has specific permission(s).

**Endpoint:** `POST /api/users/check-permission/`

**Authentication:** Not required (called by other services)

**Request Body (Single Permission):**

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "permission": "can_view_books"
}
```

**Request Body (Multiple Permissions):**

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "permissions": ["can_view_books", "can_add_book"]
}
```

**Success Response (200 OK) - Permission Granted:**

```json
{
  "allowed": true,
  "user_id": 1,
  "role": "LIBRARIAN"
}
```

**Success Response (200 OK) - Permission Denied:**

```json
{
  "allowed": false,
  "user_id": 1,
  "role": "MEMBER",
  "missing": ["can_add_book"]
}
```

**Error Responses:**

```json
// 400 Bad Request - Missing token
{
  "allowed": false,
  "error": "Token is required"
}

// 400 Bad Request - No permission specified
{
  "allowed": false,
  "error": "No permission specified"
}

// 401 Unauthorized - Invalid token
{
  "allowed": false,
  "error": "Invalid token or user"
}
```

**Notes:**

- For single permission: checks if user has that permission
- For multiple permissions: checks if user has ALL permissions
- ADMIN users automatically have all permissions

---

## Available Permissions

### Book Management (BOOKS)

- `can_view_books` - View book catalog
- `can_add_book` - Add new books
- `can_edit_book` - Edit book information
- `can_delete_book` - Delete books

### Loan Management (LOANS)

- `can_view_loans` - View own loans
- `can_borrow_book` - Borrow books
- `can_return_book` - Return borrowed books
- `can_view_all_loans` - View all loans (all users)
- `can_manage_loans` - Manage loans (approve, extend, etc.)

### User Management (USERS)

- `can_view_users` - View user list
- `can_add_user` - Add new users
- `can_edit_user` - Edit user information
- `can_delete_user` - Delete users

### Reports (REPORTS)

- `can_view_reports` - View reports
- `can_export_reports` - Export reports

---

## Default Roles & Permissions

### MEMBER

- can_view_books
- can_borrow_book
- can_return_book
- can_view_loans (own loans only)

### LIBRARIAN

- can_view_books
- can_add_book
- can_edit_book
- can_delete_book
- can_view_all_loans
- can_manage_loans
- can_view_users
- can_view_reports

### ADMIN

- All permissions (automatic)

---

## Error Codes

| Code | Description                          |
| ---- | ------------------------------------ |
| 200  | Success                              |
| 201  | Created                              |
| 400  | Bad Request (validation error)       |
| 401  | Unauthorized (invalid/missing token) |
| 403  | Forbidden (insufficient permissions) |
| 404  | Not Found                            |
| 500  | Internal Server Error                |

---

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting in production:

- Registration: 5 per hour per IP
- Login: 10 per hour per IP
- Token refresh: 100 per hour per user

---

## CORS Configuration

**Development:** All origins allowed

**Production:** Configure specific origins in settings:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]
```

---

## Example Usage

### Complete Registration Flow

```bash
# 1. Register new user
curl -X POST http://localhost:8001/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "john",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Response includes tokens
# Save access_token and refresh_token

# 2. Get current user info
curl -X GET http://localhost:8001/api/users/me/ \
  -H "Authorization: Bearer <access_token>"

# 3. Update profile
curl -X PUT http://localhost:8001/api/users/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Book lover",
    "address": "123 Main St"
  }'
```

### Microservice Integration Example

```python
# Book Service checking if user can add books
import requests

def validate_user_permission(token, permission):
    response = requests.post(
        "http://localhost:8001/api/users/check-permission/",
        json={"token": token, "permission": permission}
    )
    return response.json()["allowed"]

# Usage in Book Service
if validate_user_permission(request_token, "can_add_book"):
    # Allow book creation
    pass
else:
    # Return 403 Forbidden
    pass
```
