# Bakery Management API (v0 - In Development)

This project is a RESTful API built for the comprehensive management of a bakery. It handles raw material inventory (ingredients), the finished products catalog, dynamic recipe costing, and measurement units.

The project is currently in its **Development Phase (v0)**.

## 🛠️ Core Technologies

* **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (Operating 100% in Async mode)
* **Data Validation:** Pydantic (V2)
* **Containers:** Docker & Docker Compose (For local infrastructure)

## 📂 Project Structure

The project follows a layered architecture (Separation of Concerns) to keep the codebase clean and scalable:

```text
BAKERY-MANAGEMENT-API/
├── app/
│   ├── api/        # Routers (FastAPI Endpoints)
│   ├── db/         # Async database session configuration
│   ├── models/     # Physical SQLAlchemy models (Tables & ORM)
│   ├── schemas/    # Logical Pydantic models (Input/Output validation)
│   ├── services/   # Business logic and database queries (CRUD)
│   └── main.py     # Application entry point
├── docker-compose.yml # Infrastructure (PostgreSQL database)
├── .env.example    # Environment variables template
└── requirements.txt # Python dependencies
```

## 🚀 Getting Started

### 1. Start PostgreSQL with Docker Compose

```bash
docker compose up -d
```

This command launches the PostgreSQL service defined in `docker-compose.yml`.

### 2. Start the FastAPI server

From the project root directory:

```bash
fastapi dev
```

This starts the FastAPI development server using the local project configuration.

## 🌐 API Documentation

Once the server is running, the interactive API documentation is available at:

- `http://127.0.0.1:8000/docs`

## 📝 Notes

- The project is currently in version **0.0.0** and is still in progress.
- Expect ongoing changes to models, services, and endpoints as development continues.
- The current setup assumes a local Docker Compose-based PostgreSQL instance.
- Configure database credentials in `.env` or use the sample `.env.example` values before starting the app.
- Dependencies are defined in `requirements.txt`; install them with `pip install -r requirements.txt`.
- The local PostgreSQL service is exposed on port `5433` and connected via SQLAlchemy async driver.
