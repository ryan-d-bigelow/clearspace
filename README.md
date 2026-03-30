# Task Tracker

Tiny FastAPI REST service backed by SQLite in a single file: `app.py`.

## Run

```bash
make install
make dev
```

The service listens on `http://127.0.0.1:8000` and creates `tasks.db` automatically on startup.

## Interactive docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Root path redirects to docs: `http://127.0.0.1:8000/`

## Endpoints

- `POST /tasks`
- `GET /tasks`
- `PATCH /tasks/<id>`
- `DELETE /tasks/<id>`

## Quick curl test

Create a task:

```bash
curl -i http://127.0.0.1:8000/tasks \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"title":"Prepare interview solution"}'
```

List tasks:

```bash
curl -i http://127.0.0.1:8000/tasks
```

Update a task:

```bash
curl -i http://127.0.0.1:8000/tasks/1 \
  -X PATCH \
  -H 'Content-Type: application/json' \
  -d '{"is_completed":true}'
```

Delete a task:

```bash
curl -i http://127.0.0.1:8000/tasks/1 -X DELETE
```

Open the interactive docs in a browser:

```bash
open http://127.0.0.1:8000/docs
```

## Common commands

```bash
make format
make lint
make test
make check
make build
make docker-build
make docker-run
make precommit
```
