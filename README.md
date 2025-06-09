# Omnify Booking API

The **Omnify Booking API** is a FastAPI-based RESTful API for managing fitness studio class bookings. It allows users to create and view classes, book sessions, and manage authentication with JWT-based access and refresh tokens. The backend uses Tortoise ORM for database interactions, SQLite for storage, and includes middleware for CORS, rate limiting, logging, and error handling.

## Features
- **User Management**: Register users with roles (e.g., client, admin).
- **Class Management**: Create and list fitness classes with pagination.
- **Booking Management**: Book classes and view user-specific bookings.
- **Authentication**: Secure endpoints with JWT access and refresh tokens.
- **Role-Based Access**: Permissions for different roles (e.g., admin, client).
- **Database**: SQLite with Tortoise ORM and Aerich for migrations.
- **Middleware**: CORS, rate limiting, GZIP compression, timeout, and custom error handling.

## Project Structure
```
omnify/
├── .env.example              # Example environment variables
├── aerich.ini                # Aerich migration configuration
├── dir.py                    # Directory utility script
├── directory_structure.txt   # Project structure documentation
├── pyproject.toml            # Project metadata and dependencies
├── readme.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── test.db                   # SQLite database
├── app/                      # Main application
│   ├── main.py               # FastAPI application entry point
│   ├── auth/                 # Authentication permissions
│   ├── config/               # Configuration settings
│   ├── database/             # Database connection and models
│   │   ├── configs/          # Database configurations
│   │   └── models/           # Tortoise ORM models
│   ├── dependencies/         # FastAPI dependencies
│   ├── logging/              # Logging configuration
│   ├── middleware/           # Custom middleware
│   ├── routes/               # API route definitions
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   ├── utils/                # Utility functions (JWT, password hashing)
└── migrations/               # Aerich migration files
```

## Prerequisites
- Python 3.12+
- Virtualenv or Poetry
- SQLite
- Git

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Vaibhav-crux/omnify-booking-api.git
   cd omnify-booking-api
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update `.env` with your settings (e.g., `JWT_SECRET_KEY`, `DB_FILE`).

5. **Initialize Database**:
   - Run Aerich migrations:
     ```bash
     aerich init-db
     aerich migrate
     aerich upgrade
     ```

6. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```
   - Access the API at `http://127.0.0.1:8000`.
   - View interactive docs at `http://127.0.0.1:8000/docs`.


## Base URL
```
http://127.0.0.1:8000/api/v1
```

## Authentication
- **Access Token**: Required for most endpoints. Include in the `Authorization` header as `Bearer {access_token}`.
- **Refresh Token**: Used to obtain a new access token via `/api/v1/auth/refresh`.
- **How to Obtain Tokens**:
  - Register a user via `POST /api/v1/users`.
  - Log in via `POST /api/v1/users/login`.
  - Both return `access_token` and `refresh_token` in the response.

## API Endpoints

### Health Check
**GET /health**
- **Description**: Checks the API's health status.
- **Authentication**: None required.
- **Request**:
  ```
  GET /api/v1/health
  ```
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

### User Management

#### Register User
**POST /users**
- **Description**: Creates a new user with the 'client' role.
- **Request**:
  ```
  POST /api/v1/users
  Content-Type: application/json
  ```
  **Body**:
  ```json
  {
    "email": "vaibhav@gmail.com",
    "username": "vaibhav",
    "password": "securepassword123"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-string",
    "email": "vaibhav@gmail.com",
    "username": "vaibhav",
    "status": "active",
    "createdAt": "2025-06-09T17:23:00.000Z",
    "updatedAt": "2025-06-09T17:23:00.000Z",
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "roles": [
      {
        "id": "uuid-string",
        "name": "client",
        "description": "Default role for fitness studio clients",
        "status": "active"
      }
    ]
  }
  ```

#### Login User
**POST /users/login**
- **Description**: Authenticates a user and returns tokens.
- **Request**:
  ```
  POST /api/v1/users/login
  Content-Type: application/json
  ```
  **Body**:
  ```json
  {
    "email": "vaibhav@gmail.com",
    "password": "securepassword123"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": "uuid-string",
    "email": "vaibhav@gmail.com",
    "username": "vaibhav",
    "status": "active",
    "createdAt": "2025-06-09T17:23:00.000Z",
    "updatedAt": "2025-06-09T17:23:00.000Z",
    "access_token": "jwt-access-token",
    "refresh_token": "jwt-refresh-token",
    "roles": [
      {
        "id": "uuid-string",
        "name": "client",
        "status": "active",
        "description": "Default role for fitness studio clients"
      }
    ]
  }
  ```

#### List All Users
**GET /users**
- **Description**: Retrieves all users (admin access may be required based on permissions).
- **Request**:
  ```
  GET /api/v1/users
  Authorization: Bearer {access_token}
  ```
- **Response** (200 OK):
  ```json
  [
    {
      "id": "uuid-string",
      "email": "vaibhav@gmail.com",
      "username": "vaibhav",
      "status": "active",
      "createdAt": "2025-06-09T17:23:00.000Z",
      "updatedAt": "2025-06-09T17:23:00.000Z",
      "access_token": "",
      "refresh_token": "",
      "roles": [
        {
          "id": "uuid-string",
          "name": "client",
          "description": "Default role for fitness studio clients",
          "status": "active"
        }
      ]
    }
  ]
  ```

#### Get User by ID
**GET /users/{user_id}**
- **Description**: Retrieves a specific user by ID.
- **Request**:
  ```
  GET /api/v1/users/{uuid-string}
  Authorization: Bearer {access_token}
  ```
- **Response** (200 OK):
  ```json
  {
    "id": "uuid-string",
    "email": "vaibhav@gmail.com",
    "username": "vaibhav",
    "status": "active",
    "createdAt": "2025-06-09T17:23:00.000Z",
    "updatedAt": "2025-06-09T17:23:00.000Z",
    "access_token": "",
    "refresh_token": "",
    "roles": [
      {
        "id": "uuid-string",
        "name": "client",
        "description": "Default role for fitness studio clients",
        "status": "active"
      }
    ]
  }
  ```

#### Update User
**PATCH /users/{user_id}**
- **Description**: Updates user details, including roles.
- **Request**:
  ```
  PATCH /api/v1/users/{uuid-string}
  Content-Type: application/json
  Authorization: Bearer {access_token}
  ```
  **Body**:
  ```json
  {
    "username": "vaibhav_updated",
    "roles": ["client", "instructor"]
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": "uuid-string",
    "email": "vaibhav@gmail.com",
    "username": "vaibhav_updated",
    "status": "active",
    "createdAt": "2025-06-09T17:23:00.000Z",
    "updatedAt": "2025-06-09T17:30:00.000Z",
    "access_token": "",
    "refresh_token": "",
    "roles": [
      {
        "id": "uuid-string",
        "name": "client",
        "description": "Default role for fitness studio clients",
        "status": "active"
      },
      {
        "id": "uuid-string",
        "name": "instructor",
        "description": "Instructor role",
        "status": "active"
      }
    ]
  }
  ```

### Authentication Management

#### Refresh Token
**POST /auth/refresh**
- **Description**: Generates a new access token using a refresh token.
- **Request**:
  ```
  POST /api/v1/auth/refresh
  Content-Type: application/json
  ```
  **Body**:
  ```json
  {
    "refresh_token": "jwt-refresh-token"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": "uuid-string",
    "email": "vaibhav@gmail.com",
    "username": "vaibhav",
    "status": "active",
    "createdAt": "2025-06-09T17:23:00.000Z",
    "updatedAt": "2025-06-09T17:23:00.000Z",
    "access_token": "new-jwt-access-token",
    "refresh_token": "new-jwt-refresh-token",
    "roles": [
      {
        "id": "uuid-string",
        "name": "client",
        "description": "Default role for fitness studio clients",
        "status": "active"
      }
    ]
  }
  ```

#### Revoke Token
**POST /auth/revoke**
- **Description**: Invalidates a refresh token to log out.
- **Request**:
  ```
  POST /api/v1/auth/revoke
  Content-Type: application/json
  ```
  **Body**:
  ```json
  {
    "refresh_token": "jwt-refresh-token"
  }
  ```
- **Response** (204 No Content):
  ```json
  {}
  ```

### Role Management

#### Create Role
**POST /roles**
- **Description**: Creates a new role.
- **Request**:
  ```
  POST /api/v1/roles
  Content-Type: application/json
  Authorization: Bearer {access_token}
  ```
  **Body**:
  ```json
  {
    "name": "instructor",
    "description": "Instructor role for teaching classes"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-string",
    "name": "instructor",
    "description": "Instructor role for teaching classes",
    "status": "active",
    "createdAt": "2025-06-09T17:23:00.000Z",
    "updatedAt": "2025-06-09T17:23:00.000Z"
  }
  ```

#### List Roles
**GET /roles**
- **Description**: Retrieves all roles, optionally filtered by status.
- **Request**:
  ```
  GET /api/v1/roles?status=active
  Authorization: Bearer {access_token}
  ```
- **Response** (200 OK):
  ```json
  [
    {
      "id": "uuid-string",
      "name": "client",
      "description": "Default role for fitness studio clients",
      "status": "active",
      "createdAt": "2025-06-09T17:23:00.000Z",
      "updatedAt": "2025-06-09T17:23:00.000Z"
    }
  ]
  ```

#### Update Role
**PATCH /roles/{role_id}**
- **Description**: Updates a role’s details.
- **Request**:
  ```
  PATCH /api/v1/roles/{uuid-string}
  Content-Type: application/json
  Authorization: Bearer {access_token}
  ```
  **Body**:
  ```json
  {
    "description": "Updated instructor role description"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": "uuid-string",
    "name": "instructor",
    "description": "Updated instructor role description",
    "status": "active",
    "createdAt": "2025-06-09T17:23:00.000Z",
    "updatedAt": "2025-06-09T17:30:00.000Z"
  }
  ```

#### Delete Role
**DELETE /roles/{role_id}**
- **Description**: Deletes a role.
- **Request**:
  ```
  DELETE /api/v1/roles/{uuid-string}
  Authorization: Bearer {access_token}
  ```
- **Response** (204 No Content):
  ```json
  {}
  ```

### Class Management

#### Create Class
**POST /classes**
- **Description**: Creates a new fitness class with the authenticated user as the instructor.
- **Request**:
  ```
  POST /api/v1/classes
  Content-Type: application/json
  Authorization: Bearer {access_token}
  ```
  **Body**:
  ```json
  {
  "name": "Yoga",
  "schedule": "2025-06-15T10:00:00+05:30",
  "slots": 10
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-string",
    "name": "Yoga",
    "date": "2025-06-10",
    "time": "10:00:00",
    "instructor": "vaibhav",
    "available_slots": 10,
    "status": "active",
    "timezone": "Asia/Kolkata"
  }
  ```

#### List Classes
**GET /classes**
- **Description**: Retrieves paginated fitness classes with pagination parameters.
- **Request**:
  ```
  GET /api/v1/classes?page=1&limit=2
  Authorization: Bearer {access_token}
  ```
- **Response** (200 OK):
  ```json
  {
    "items": [
      {
        "id": "uuid-string",
        "name": "Yoga",
        "date": "2025-06-10",
        "time": "10:00:00",
        "instructor": "vaibhav",
        "available_slots": 10,
        "status": "active",
        "timezone": "Asia/Kolkata"
      }
    ],
    "total": 1,
    "page": 1,
    "limit": 2,
    "total_pages": 1
  }
  ```

### Booking Management

#### Create Booking
**POST /book**
- **Description**: Books a class for the authenticated user.
- **Request**:
  ```
  POST /api/v1/book
  Content-Type: application/json
  Authorization: Bearer {access_token}
  ```
  **Body**:
  ```json
  {
    "class_id": "uuid-string",
    "client_name": "Vaibhav",
    "client_email": "vaibhav@gmail.com"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-string",
    "class_id": "uuid-string",
    "class_name": "Yoga",
    "class_date": "2025-06-10",
    "class_time": "10:00:00",
    "client_name": "Vaibhav",
    "client_email": "vaibhav@gmail.com",
    "status": "active",
    "timezone": "Asia/Kolkata"
  }
  ```

#### List Bookings
**GET /bookings**
- **Description**: Retrieves all bookings for the authenticated user.
- **Request**:
  ```
  GET /api/v1/bookings
  Authorization: Bearer {access_token}
  ```
- **Response** (200 OK):
  ```json
  [
    {
      "id": "uuid-string",
      "class_id": "uuid-string",
      "class_name": "Yoga",
      "class_date": "2025-06-10",
      "class_time": "10:00:00",
      "client_name": "vaibhav",
      "client_email": "vaibhav@gmail.com",
      "status": "active"
    }
  ]
  ```

## Setup Instructions
1. **Install Dependencies**:
   ```bash
   pip install fastapi tortoise-orm[aiosqlite] PyJWT bcrypt>=4.0.1 passlib>=1.7.4 uvicorn
   ```
2. **Run Migrations**:
   ```bash
   aerich init -t app.database.connection.TORTOISE_ORM
   aerich init-db
   aerich migrate
   aerich upgrade
   ```
3. **Start Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
4. **Test with Postman**:
   - Use the above URLs and examples.
   - Obtain an `access_token` via `/users` or `/users/login` for authenticated requests.

## Notes
- **Permissions**: Endpoints are accessible to all authenticated users (`*`) as defined in `app/auth/permissions.py`, except where admin roles are required (e.g., role management).
- **Error Handling**: Common errors include:
  - `401 Unauthorized`: Invalid or missing token.
  - `404 Not Found`: Resource (e.g., user, class) not found.
  - `409 Conflict`: Duplicate resource (e.g., email, booking).
- **Timezone**: All datetime fields use UTC (e.g., `2025-06-10T10:00:00Z`).
- **Security**: Passwords are hashed using `passlib` with bcrypt. Tokens are signed with `PyJWT`.

For issues, check logs in `app/logging/config.py`.