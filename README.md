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

## Configure environment variables

Update `.env` file based on your preferences.

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

# Deployment Requirements

Add the followings into the Github Actions:

1. `DOCKERHUB_USERNAME`
1. `DOCKERHUB_TOKEN`

These are required to push the image into Docker Hub.

# Authentication Flow

1. Register via `POST /auth/signup` with `email`, `username`, and `password`.
2. Login via `POST /auth/login` (OAuth2 password form) to receive a Bearer
   token.
3. Include the token in the `Authorization` header for protected routes:
   ```
   Authorization: Bearer <token>
   ```
