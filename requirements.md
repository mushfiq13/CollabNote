# Section A — Service Inventory

| Service(s)         | Image                                                | Port(s)              | Role                                                             |
| ------------------ | ---------------------------------------------------- | -------------------- | ---------------------------------------------------------------- |
| nginx              | nginx:1.29.7-alpine                                  | 80:80                | Acts as a Reverse Proxy and Load Balancer                        |
| fastapi1, fastapi2 | python:3.12-slim (build from inline Dockerfile)      | -                    | Container to run FastAPI application                             |
| db                 | postgres:16                                          | 5433:5432            | Containerized PostgreSQL Database                                |
| mongodb            | mongo:7.0                                            | 27017:27017          | Containerized NoSQL Database                                     |
| elasticsearch      | docker.elastic.co/elasticsearch/elasticsearch:8.11.1 | 9200:9200, 9300:9300 | ElasticSearch to fast lookup                                     |
| redis              | redis:7-alpine                                       | 6379:6379            | In-memory key-value paired cache database                        |
| kafka              | confluentinc/cp-kafka:7.6.0                          | 9092:9092            | Event Streaming Service with 1 broker and partition              |
| consumer           | python:3.12-slim (build from inline Dockerfile)      | -                    | Consumer to read logs from Kafka                                 |
| migration          | python:3.12-slim (build from inline Dockerfile)      | -                    | Run Alembic migrations on startup and stop the service once done |

# Section B - Resource Estimate

| Services           | Min RAM (MB)     | Min CPU (Cores) | Notes                                                |
| ------------------ | ---------------- | --------------- | ---------------------------------------------------- |
| nginx              | 64               | 0.1             | Lightweight reverse proxy and load balancer          |
| fastapi1, fastapi2 | 256              | 0.5             | API application instances; scales with traffic       |
| db (PostgreSQL)    | 512              | 0.5             | Relational database workload with persistent storage |
| mongodb            | 512              | 0.5             | NoSQL database with moderate memory usage            |
| elasticsearch      | 1024             | 1.0             | Memory-intensive search and indexing service         |
| redis              | 128              | 0.2             | In-memory cache for fast key-value operations        |
| kafka              | 1024             | 1.0             | Event streaming broker; requires stable CPU and RAM  |
| consumer           | 256              | 0.3             | Background Kafka consumer processing messages        |
| migration          | 128              | 0.1             | One-time job for running database migrations         |
| TOTAL              | ~3904 MB (~4 GB) | ~4.2 Cores      | Request VM with 4 GB RAM / 4 vCPU                    |

# Section C - Data Model Summary

`users` **Table:** Store user credentials and used for authorization purpose.
`db` service provides PostgreSQL database to store these user data.

| Field         | Type         | Description                 |
| ------------- | ------------ | --------------------------- |
| id            | Integer (PK) | Unique user identifier      |
| email         | String(255)  | Unique email for login      |
| username      | String(50)   | Unique display/handle       |
| password_hash | String       | Secure hashed password      |
| role          | String       | User role (`user`, `admin`) |
| is_active     | Boolean      | Account status              |
| created_at    | DateTime     | Account creation timestamp  |

`notes` **Collection:** Used to write/read notes.

- `mongodb` service acts as a source-of-truth for notes.
- `elasticsearch` service stores the notes for fast lookup.

| Field      | Type                    | Description            |
| ---------- | ----------------------- | ---------------------- |
| \_id       | ObjectId (string alias) | Unique note identifier |
| title      | String                  | Note title             |
| content    | String                  | Main note body         |
| tags       | List[String]            | Categorization labels  |
| created_at | DateTime                | Creation timestamp     |

`logs` **Collection:**

- `kafka` service stores these logs.
- `mongodb` service stores logs via `consumer` service.

| Field     | Type              | Description                           |
| --------- | ----------------- | ------------------------------------- |
| \_id      | ObjectId          | Unique event record ID                |
| user_id   | String            | User who performed action             |
| action    | String            | Event type (login, create_note, etc.) |
| resource  | String (optional) | Target resource ID                    |
| details   | Dict              | Extra contextual metadata             |
| timestamp | DateTime          | Event time                            |
| metadata  | Dict              | System-level info (IP, device, etc.)  |

# Section D - Endpoint Inventory

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

# Section E - Architecture Decision Log (ADL)

## Storing Notes

**Context:** Notes contain unstructured data, the data-structure can be changed
rapidly.

**Decision:** Notes are stored in MongoDB instead of PostgreSQL.

**Rationale:** We need something which allows us to change the schema
dynamically. Therefore MongoDB is the right choice which gives us flexibility.

## Clearing Stale Cached Data

**Context:** We are using Redis to cache data which are static and not meant to
change frequently.

**Decision:** Set TTL to one hour rather than indefinite.

**Rationale:** We cannot guarantee that the cached value would be valid for
lifetime, may be the user account is deleted or in offline for a few days/weeks.
So in this cases just storing the data becomes stale and brings memory
bottleneck. Instead lets clear the cached values after a certain period (in our
case 1 hour).

## Consume Events by Dedicated Consumer Processor

**Context:** We need a background processor to read the data from Kafka and save
into DB.

**Decision:** Run Kafka consumer as a separate process rather than a FastAPI
background task.

**Rationale:** Consumer runs continuously to read the data from Kafka server.
Imagine the subscription process is implemented inside a FastAPI instance and if
the background workloads becomes too high, then we may have to run multiple
FastAPI instances or may have to scale the API layer.

In this case, a Consumer service is a better choice that is dedicated to load
heavy works.

## Using Elasticsearch for Fast Lookup

**Context:** We need efficient and fast search capabilities for notes.

**Decision:** Use Elasticsearch for search and indexing instead of relying on
MongoDB queries.

**Rationale:** MongoDB is optimized for data storage and basic queries, but it
is not ideal for advanced full-text search at scale. Elasticsearch is
specifically designed for fast, indexed search operations and provides better
performance and relevance scoring for search use cases.
