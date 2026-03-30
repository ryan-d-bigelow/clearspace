# Task Tracker

Modular FastAPI REST service backed by SQLite.

The root [app.py](/Users/ryanbigelow/source/wevo/repos/clearspace/app.py) is now only a thin entrypoint. The actual app lives under `src/task_tracker`.

## Run

```bash
make install
make dev
```

The service listens on `http://127.0.0.1:8000` and creates `tasks.db` automatically on startup.

## Architecture

```text
src/task_tracker
├── app.py                  # App factory + top-level FastAPI wiring
├── api
│   ├── dependencies.py     # Shared dependency providers
│   ├── errors.py           # Shared API error shaping
│   └── router.py           # Central router registration
├── core
│   ├── config.py           # Environment/runtime settings
│   └── exceptions.py       # Framework-agnostic domain errors
├── db
│   ├── bootstrap.py        # Runs all module schema initializers
│   └── sqlite.py           # Shared SQLite connection wrapper
└── modules
    ├── _template
        │   ├── api.py          # Copy this package for the next module
    │   ├── dtos.py         # Storage/domain transfer objects
    │   ├── models.py       # ORM models
    │   ├── repository.py   # Stub storage layer
    │   ├── schema.py       # Stub table bootstrap
    │   ├── schemas.py      # Stub request/response models
    │   └── service.py      # Stub business logic
    └── tasks
        ├── api.py          # Task routes
        ├── dtos.py         # DTO layer between storage and API
        ├── models.py       # SQLAlchemy ORM models
        ├── repository.py   # SQL/data access
        ├── schema.py       # Task table initialization
        ├── schemas.py      # Pydantic models
        └── service.py      # Business logic
```

## Extension points

- Add new routes in `src/task_tracker/modules/<module_name>/api.py`.
- Add request/response models in `src/task_tracker/modules/<module_name>/schemas.py`.
- Add DTOs in `src/task_tracker/modules/<module_name>/dtos.py`.
- Add ORM models in `src/task_tracker/modules/<module_name>/models.py`.
- Add business logic in `src/task_tracker/modules/<module_name>/service.py`.
- Add SQLAlchemy data access in `src/task_tracker/modules/<module_name>/repository.py`.
- Add table creation in `src/task_tracker/modules/<module_name>/schema.py`.
- Register the module router in `src/task_tracker/api/router.py`.
- Register the module schema initializer in `src/task_tracker/app.py`.
- Add shared framework config in `src/task_tracker/core/config.py`.
- Add reusable app-wide helpers and dependencies in `src/task_tracker/api/` or `src/task_tracker/db/`.

## Adding a new full-stack module

Use `tasks` as the concrete example and `src/task_tracker/modules/_template` as the starter scaffold.

1. Copy `src/task_tracker/modules/_template` to `src/task_tracker/modules/<module_name>`.
2. Rename the placeholder `Widget*` symbols to your domain terms.
3. Fill in `models.py` with the module's ORM models.
4. Fill in `dtos.py` with the module's repository/service transfer shapes.
5. Fill in `repository.py` with module-specific SQLAlchemy persistence code.
6. Fill in `service.py` with module-specific business logic.
7. Add any module tables in `schema.py`.
8. Include the router from `src/task_tracker/api/router.py`.
9. Add the schema initializer to `SCHEMA_INITIALIZERS` in `src/task_tracker/app.py`.

That gives each feature a clear `api / service / dto / model / repository / schema`
slice without mixing framework concerns and business concerns.

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
