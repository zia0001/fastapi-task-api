# fastapi-task-api

A simple RESTful CRUD API built with FastAPI, PostgreSQL, and Docker. The project demonstrates Create, Read, Update, and Delete operations with request validation, proper HTTP status codes, interactive Swagger UI documentation, persistent database storage, and a containerized application stack.

## Features

* Create a new task
* Read all tasks
* Read a task by ID
* Update an existing task
* Delete a task
* Input validation using Pydantic
* Proper HTTP status codes
* Interactive Swagger UI documentation
* PostgreSQL database persistence
* PostgreSQL running in Docker
* Persistent Docker volume for database data
* Automatic database and table creation
* Automatic seeding of example tasks when the database is empty
* Application and database start together with Docker Compose
* Data survives application and container restarts

---

## Technologies Used

* Python 3.x
* FastAPI
* Uvicorn
* Pydantic
* PostgreSQL
* Psycopg
* Docker
* Docker Compose

---

## Project Structure

```text
fastapi-task-api/

│
├── screenshots/
│   ├── swagger-ui.png
│   └── database.png
│
├── main.py
├── database.py
├── init.sql
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── requirements.txt
├── README.md
└── .gitignore
```

### File Responsibilities

* `main.py` — FastAPI application, API endpoints, and request validation.
* `database.py` — PostgreSQL connection, table creation, seeding, and SQL CRUD operations.
* `init.sql` — SQL script used to create the `tasks` table.
* `Dockerfile` — Builds the Docker image for the FastAPI application.
* `docker-compose.yml` — Runs the FastAPI application and PostgreSQL database together.
* `.env` — Local database configuration. This file is not committed to Git.
* `.env.example` — Example environment configuration for other developers.
* `screenshots/` — Project screenshots.

---

## Database

This project uses **PostgreSQL** for persistent data storage.

PostgreSQL runs inside a Docker container and uses a Docker volume so that database data survives container restarts.

The database configuration is provided through environment variables:

```text
POSTGRES_DB=taskdb
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpassword
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

The actual `.env` file is gitignored and is not committed to the repository.

A `.env.example` file is included so the required configuration can be recreated.

### Tasks Table

The `tasks` table contains:

| Column  | Type    | Description            |
| ------- | ------- | ---------------------- |
| `id`    | INTEGER | Primary key            |
| `title` | TEXT    | Task title             |
| `done`  | BOOLEAN | Task completion status |

The table is created with:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);
```

If the table is empty, three example tasks are automatically inserted.

---

## Architecture

The application separates the API layer from the database layer:

```text
Client
   ↓
FastAPI
   ↓
main.py
   ↓
database.py
   ↓
PostgreSQL
   ↓
Docker Volume
```

The API routes and service behavior remain unchanged while the storage implementation was switched from the previous in-memory/SQLite implementation to PostgreSQL.

This demonstrates that changing the storage layer does not require changing the API endpoints.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/zia0001/fastapi-task-api.git
```

Move into the project directory:

```bash
cd fastapi-task-api
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment.

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a local `.env` file:

```env
POSTGRES_DB=taskdb
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

The `.env` file is intentionally excluded from Git.

For Docker Compose, the application container uses:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

because the FastAPI container communicates with PostgreSQL through the Docker Compose network.

---

## Run the Project with Docker Compose

Make sure Docker is installed and running.

Build and start the complete stack:

```bash
docker compose up --build
```

This starts:

```text
FastAPI application
       +
PostgreSQL database
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## Docker Services

The Docker Compose stack contains two services:

```text
app
 │
 └── FastAPI application

postgres
 │
 └── PostgreSQL database
       │
       └── task-api-postgres-data
```

The PostgreSQL container exposes port `5433` on the host and uses port `5432` internally.

The database data is stored in the Docker volume:

```text
task-api-postgres-data
```

This volume ensures that database data is not lost when the PostgreSQL container is restarted.

---

## API Endpoints

| Method | Endpoint           | Description             |
| ------ | ------------------ | ----------------------- |
| GET    | `/`                | API information         |
| GET    | `/health`          | Health check            |
| GET    | `/tasks`           | Retrieve all tasks      |
| GET    | `/tasks/{task_id}` | Retrieve a task by ID   |
| POST   | `/tasks`           | Create a new task       |
| PUT    | `/tasks/{task_id}` | Update an existing task |
| DELETE | `/tasks/{task_id}` | Delete a task           |

All CRUD operations now operate on PostgreSQL rather than an in-memory Python list.

---

## Example cURL Request

Get all tasks:

```bash
curl -i http://127.0.0.1:8000/tasks
```

Example response:

```json
[
  {
    "id": 1,
    "title": "Study FastAPI",
    "done": false
  },
  {
    "id": 2,
    "title": "Buy groceries",
    "done": true
  },
  {
    "id": 3,
    "title": "Complete assignment",
    "done": false
  }
]
```

---

## PostgreSQL Database Inspection

The PostgreSQL database can be accessed directly through `psql`.

For example:

```bash
docker exec -it task-api-postgres-1 psql -U taskuser -d taskdb
```

View the available tables:

```sql
\dt
```

Inspect the `tasks` table:

```sql
\d tasks
```

View all tasks:

```sql
SELECT * FROM tasks;
```

Example:

```text
 id |        title        | done
----+---------------------+------
  1 | Study FastAPI       | f
  2 | Buy groceries       | t
  3 | Complete assignment | f
```

---

## HTTP Status Codes

| Status Code | Meaning                       |
| ----------- | ----------------------------- |
| 200         | Successful request            |
| 201         | Resource created              |
| 204         | Resource deleted successfully |
| 400         | Invalid request               |
| 404         | Resource not found            |

---

## Swagger UI

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Screenshot

![Swagger UI](screenshots/swagger-ui.png)

---

## Database Screenshot

The PostgreSQL database and `tasks` table were inspected directly using `psql`.

![Database](screenshots/database.png)

---

## Persistence Test

Database persistence was tested by creating tasks and then restarting the application and PostgreSQL container.

The process was:

```text
Create tasks
     ↓
Tasks stored in PostgreSQL
     ↓
Stop containers
     ↓
Start containers again
     ↓
PostgreSQL uses existing Docker volume
     ↓
Tasks are still available
```

The PostgreSQL container reported:

```text
PostgreSQL Database directory appears to contain a database;
Skipping initialization
```

after restarting, confirming that the existing database data was preserved.

The Docker volume used for persistence is:

```text
task-api-postgres-data
```

The volume remains separate from the application container, allowing database data to survive container restarts.

---

## Docker Compose

The complete application stack can be started with one command:

```bash
docker compose up
```

For a fresh image build:

```bash
docker compose up --build
```

To stop the stack:

```bash
docker compose down
```

The Docker volume is intentionally preserved when using:

```bash
docker compose down
```

Therefore, the PostgreSQL data remains available when the stack is started again.

---

## A3 Architecture Result

This assignment demonstrates the transition from a simple CRUD application to a containerized backend stack:

```text
A2

FastAPI
   ↓
In-memory / local storage


        ↓


A3

FastAPI
   ↓
PostgreSQL Repository
   ↓
PostgreSQL
   ↓
Docker
   ↓
Persistent Docker Volume
```

The API routes were kept unchanged while the storage implementation was replaced with PostgreSQL.

This proves that the application can switch its persistence layer without changing the API interface.

---

## Author

**Zia Uddin**

GitHub: https://github.com/zia0001

````

### One important correction

Your old README included `tasks.db`. **Remove that from the A3 project structure**. Your A3 database is PostgreSQL now, so `tasks.db` is no longer part of the application's storage.

Also make sure you **do not commit `.env`**. Only `.env.example` should go to GitHub.

After replacing the README:

```bash
git status
````

Then:

```bash
git add README.md database.py main.py requirements.txt Dockerfile docker-compose.yml init.sql .dockerignore .env.example screenshots/
git commit -m "A3: containerize FastAPI with PostgreSQL"
git push origin main
```

Then your GitHub repository is ready to submit as the A3 proof.
