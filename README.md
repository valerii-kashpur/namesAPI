# 🌍 NamesAPI

![Python](https://img.shields.io/badge/python-3.11+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg) ![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg)

**NamesAPI** is a secure REST API built with [FastAPI](https://fastapi.tiangolo.com/) that fetches and manages
name-related data by integrating with external APIs like [Nationalize.io](https://nationalize.io/)
and [REST Countries](https://restcountries.com/). It allows you to retrieve countries associated with a given name and
find the most popular names for a specific country. The API is protected with authentication, requiring users to
register or log in to access the core functionality.

## 🚀 Features

- 🔒 **User Authentication**: Register and log in to access protected endpoints.
- **Name-to-Country Mapping**: Get a list of countries associated with a name, along with probabilities (requires
  authentication).
- **Popular Names by Country**: Retrieve the top 5 most popular names for a given country (requires authentication).
- **FastAPI-Powered**: Built with FastAPI for high performance and auto-generated API docs.
- **Dockerized**: Easy deployment with Docker and Docker Compose.
- **Tested**: Includes unit and integration tests with `pytest`.

## 📋 Prerequisites

Before you start, ensure you have the following installed:

- 🛠️ **Git** (to clone the repository)
- 🐳 **Docker** and **Docker Compose** (to run the application)
- 🐍 **Python 3.11+** (for running tests locally outside Docker)
- ✅ **pytest** (for running tests, installed via `pip`)
- 🌐 **curl** or a tool like [Postman](https://www.postman.com/) (to test API endpoints with authentication)

## 🛠️ Installation & Setup

Follow these steps to get the project up and running.

### 1. Clone the Repository

Clone the `dev` branch of the repository:

```bash
git clone -b dev https://github.com/valerii-kashpur/namesAPI.git
cd namesAPI
```

## 🔍 Required environment via .env

- **Create .env with cred below**:

  ```bash
  POSTGRES_USER=user
  POSTGRES_PASSWORD=password
  POSTGRES_DB=names_db
  
  DATABASE_URL=postgresql://user:password@db:5432/names_db
  
  SECRET_KEY=your-very-secure-random-key-here-1234567890abcdef
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  ```

### 2. Run the Application with Docker

To run the application using Docker:

1. Ensure Docker and Docker Compose are running on your machine.
2. Build and start the containers:

   ```bash
   docker-compose up --build
   ```

3. The application will be available at:

   ```
   http://localhost:8000
   ```

### 3. Explore the API Documentation

NamesAPI provides auto-generated API documentation via FastAPI's Swagger UI. Once the application is running, visit:

```
http://localhost:8000/docs
```

You'll find an interactive interface to explore and test the API endpoints. Note that protected endpoints (`/names/` and
`/popular-names/`) require authentication, which you can set up using the `/auth/register` and `/auth/login` endpoints (
see below).

## 🔐 Authentication Setup

To access the core functionality of NamesAPI (name-related endpoints), you need to authenticate by registering or
logging in. The API uses JWT tokens for authorization.

### Step 1: Register a New User

Use the `/auth/register` endpoint to create a new user account:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "securepassword123"}'
```

**Response** (example):

```json
{
  "access_token": "your_jwt_token",
  "token_type": "bearer"
}
```

### Step 2: Log In

If you already have an account, log in using the `/auth/login` endpoint:

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "securepassword123"}'
```

**Response** (example):

```json
{
  "access_token": "your_jwt_token",
  "token_type": "bearer"
}
```

### Step 3: Use the Token

To access protected endpoints, include the JWT token in the `Authorization` header of your requests:

```
Authorization: Bearer your_jwt_token
```

You can test this in the Swagger UI (`http://localhost:8000/docs`) by clicking the "Authorize" button and entering your
token.

## 📌 API Endpoints

Here are the main endpoints provided by NamesAPI:

| Endpoint                             | Description                           | Requires Auth | Example Response                                           |
|--------------------------------------|---------------------------------------|---------------|------------------------------------------------------------|
| `POST /auth/register`                | Register a new user                   | No            | `{"access_token": "...", "token_type": "bearer"}`          |
| `POST /auth/login`                   | Log in and get a JWT token            | No            | `{"access_token": "...", "token_type": "bearer"}`          |
| `GET /names/?name=<name>`            | Get countries associated with a name  | Yes           | `[{"name": "Jake", "country": {...}, "probability": 0.7}]` |
| `GET /popular-names/?country=<code>` | Get top 5 popular names for a country | Yes           | `[{"name": "John", "count": 10}]`                          |

### Example Usage (Authenticated Requests)

- **Get countries for a name** (requires token):

  ```bash
  curl http://localhost:8000/names/?name=jake \
    -H "Authorization: Bearer your_jwt_token"
  ```

- **Get popular names for a country** (requires token):

  ```bash
  curl http://localhost:8000/popular-names/?country=US \
    -H "Authorization: Bearer your_jwt_token"
  ```

## ✅ Run Tests

To run the project's tests with `pytest`:

1. Ensure the application containers are running (from step 2), as tests may depend on the database.
2. Open a terminal in the project directory and run:

   ```bash
   pytest src/tests
   ```

   This will execute all tests in the `src/tests` directory and display the results.

> **Note**: If you encounter dependency issues, install them locally:
>
> ```bash
> pip install -r requirements.txt
> pip install pytest
> ```

## 📂 Project Structure

Here's an overview of the project's structure:

```
namesAPI/
├── src/
│   ├── api/              # API routes and endpoints (including auth routes)
│   ├── clients/          # HTTP clients for external APIs
│   ├── database/         # Database models and setup
│   ├── exceptions/       # Custom exception handling
│   ├── repositories/     # Database operations
│   ├── services/         # Business logic (including auth service)
│   ├── tests/            # Unit and integration tests
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```