# Introduction

CollabNote is a production-grade, collaborative notes API. Every architectural
decision reflects patterns used in real-world systems at companies like Notion,
Linear, and Confluence.

The entire stack runs behind an Nginx load balancer, is containerized with
Docker Compose, and is deployed automatically through a GitHub Actions CI/CD
pipeline.

# Key User Flows

The following five flows cover the full lifecycle of the system and are used as
acceptance criteria:

1. User registers via POST /auth/signup → profile stored in PostgreSQL → Kafka
   publishes signup event → consumer logs it to MongoDB.
1. Authenticated user creates a note via POST /notes → document stored in
   MongoDB → indexed in Elasticsearch → cache invalidated → Kafka publishes
   create_note event.
1. User searches via GET /search?q=fastapi → Elasticsearch returns
   fuzzy-matched, ranked results with highlighted snippets.
1. User reads a hot note via GET /notes/{id} → Redis cache hit returns data in <
   2 ms; on cache miss, MongoDB is queried, and the result is cached.

# Tech Stack

| Layer             | Technology                            |
| ----------------- | ------------------------------------- |
| Framework         | FastAPI                               |
| ASGI Server       | Uvicorn                               |
| Relational DB     | PostgreSQL (via SQLAlchemy + Alembic) |
| Document DB       | MongoDB (via Motor — async)           |
| Auth              | JWT (python-jose) + bcrypt (passlib)  |
| Validation        | Pydantic v2                           |
| Streaming Service | Kafka                                 |
| Caching           | Redis                                 |
| Load Balancer     | Nginx                                 |

# Setup Instructions

## Configure environment variables [Required]

Copy `.env.example` to `.env` and fill in your values.

## Run via Docker

```sh
docker compose up --build -d
```

## Run via Local Machine

**Clone and create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Run database migrations**

```bash
alembic upgrade head
```

**Start the server**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:80`. Interactive docs:
`http://localhost:80/docs`

# API Endpoints

## Root & Health

| Method | Path      | Description   |
| ------ | --------- | ------------- |
| GET    | `/`       | Root endpoint |
| GET    | `/health` | Health check  |
| GET    | `/ping`   | Ping service  |

## Authentication

| Method | Path           | Description                   |
| ------ | -------------- | ----------------------------- |
| POST   | `/auth/signup` | Register a new user           |
| POST   | `/auth/login`  | Login and receive a JWT token |

## Profile

| Method | Path       | Description      |
| ------ | ---------- | ---------------- |
| GET    | `/profile` | Get user profile |

## Users

| Method | Path               | Description    |
| ------ | ------------------ | -------------- |
| GET    | `/users`           | Get all users  |
| GET    | `/users/{user_id}` | Get user by ID |
| PUT    | `/users/{user_id}` | Update user    |
| DELETE | `/users/{user_id}` | Delete user    |

## Notes

| Method | Path               | Description    |
| ------ | ------------------ | -------------- |
| POST   | `/notes`           | Create note    |
| GET    | `/notes`           | Get all notes  |
| GET    | `/notes/{note_id}` | Get note by ID |
| PUT    | `/notes/{note_id}` | Update note    |
| DELETE | `/notes/{note_id}` | Delete note    |

## Search

| Method | Path      | Description  |
| ------ | --------- | ------------ |
| GET    | `/search` | Search notes |

## Cache

| Method | Path           | Description      |
| ------ | -------------- | ---------------- |
| GET    | `/cache/stats` | Cache statistics |
| DELETE | `/cache/notes` | Clear cache      |

## Users (Admin)

| Method | Path                    | Description   |
| ------ | ----------------------- | ------------- |
| GET    | `/users/{user_id}/logs` | Get user logs |

## Logs

| Method | Path          | Description             |
| ------ | ------------- | ----------------------- |
| POST   | `/logs`       | Create log event        |
| GET    | `/logs`       | Get logs (latest first) |
| GET    | `/logs/stats` | Get log statistics      |

# Authentication Flow

1. Register via `POST /auth/signup` with `email`, `username`, and `password`.
2. Login via `POST /auth/login` (OAuth2 password form) to receive a Bearer
   token.
3. Include the token in the `Authorization` header for protected routes:
   ```
   Authorization: Bearer <token>
   ```
