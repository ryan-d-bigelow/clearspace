import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import create_app, fetch_task_by_id, format_validation_error, get_connection


@pytest.fixture
def client(tmp_path) -> TestClient:
    database_path = tmp_path / "tasks.db"
    app = create_app(str(database_path))

    with TestClient(app) as test_client:
        yield test_client


def test_database_initializes_on_startup(tmp_path) -> None:
    database_path = tmp_path / "tasks.db"

    app = create_app(str(database_path))
    with TestClient(app):
        pass

    connection = sqlite3.connect(database_path)
    try:
        row = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'tasks'"
        ).fetchone()
    finally:
        connection.close()

    assert row == ("tasks",)


def test_root_lists_available_endpoints(client) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_openapi_json_describes_task_routes(client) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["openapi"] == "3.1.0"
    assert "/tasks" in response.json()["paths"]
    assert "/tasks/{task_id}" in response.json()["paths"]


def test_docs_route_serves_swagger_ui(client) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Swagger UI" in response.text


def test_create_task_defaults_to_not_completed(client) -> None:
    response = client.post("/tasks", json={"title": "Write solution", "ignored": "value"})

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["title"] == "Write solution"
    assert response.json()["is_completed"] is False
    assert response.json()["created_at"]


def test_create_task_rejects_empty_title(client) -> None:
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 400
    assert response.json() == {"error": "title is required and must be a non-empty string."}


def test_create_task_requires_title(client) -> None:
    response = client.post("/tasks", json={})

    assert response.status_code == 400
    assert response.json() == {"error": "title is required and must be a non-empty string."}


def test_create_task_rejects_non_object_json(client) -> None:
    response = client.post("/tasks", json=["not", "an", "object"])

    assert response.status_code == 400
    assert response.json() == {"error": "Request body must be a JSON object."}


def test_create_task_rejects_invalid_is_completed(client) -> None:
    response = client.post("/tasks", json={"title": "Write solution", "is_completed": "yes"})

    assert response.status_code == 400
    assert response.json() == {"error": "is_completed must be a boolean when provided."}


def test_list_tasks_returns_newest_first(client) -> None:
    client.post("/tasks", json={"title": "First"})
    client.post("/tasks", json={"title": "Second"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Second", "First"]


def test_patch_updates_known_fields_and_ignores_unknown_fields(client) -> None:
    client.post("/tasks", json={"title": "Initial"})

    response = client.patch(
        "/tasks/1",
        json={"title": "Updated", "is_completed": True, "ignored": "value"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["is_completed"] is True


def test_patch_returns_404_for_missing_task(client) -> None:
    response = client.patch("/tasks/999", json={"title": "Missing"})

    assert response.status_code == 404
    assert response.json() == {"error": "Task not found."}


def test_patch_rejects_non_object_json(client) -> None:
    response = client.patch("/tasks/1", json=["not", "an", "object"])

    assert response.status_code == 400
    assert response.json() == {"error": "Request body must be a JSON object."}


def test_patch_rejects_empty_update_payload(client) -> None:
    client.post("/tasks", json={"title": "Initial"})

    response = client.patch("/tasks/1", json={"ignored": "value"})

    assert response.status_code == 400
    assert response.json() == {"error": "At least one of title or is_completed must be provided."}


def test_patch_rejects_empty_title(client) -> None:
    client.post("/tasks", json={"title": "Initial"})

    response = client.patch("/tasks/1", json={"title": "   "})

    assert response.status_code == 400
    assert response.json() == {"error": "title must be a non-empty string when provided."}


def test_patch_rejects_null_title(client) -> None:
    client.post("/tasks", json={"title": "Initial"})

    response = client.patch("/tasks/1", json={"title": None})

    assert response.status_code == 400
    assert response.json() == {"error": "title must be a non-empty string when provided."}


def test_patch_rejects_invalid_is_completed(client) -> None:
    client.post("/tasks", json={"title": "Initial"})

    response = client.patch("/tasks/1", json={"is_completed": "yes"})

    assert response.status_code == 400
    assert response.json() == {"error": "is_completed must be a boolean when provided."}


def test_delete_removes_task(client) -> None:
    client.post("/tasks", json={"title": "Delete me"})

    response = client.delete("/tasks/1")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/tasks").json() == []


def test_delete_returns_404_for_missing_task(client) -> None:
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"error": "Task not found."}


def test_fetch_task_by_id_raises_lookup_error(tmp_path) -> None:
    database_path = tmp_path / "tasks.db"
    app = create_app(str(database_path))
    with TestClient(app):
        pass

    connection = get_connection(str(database_path))
    try:
        with pytest.raises(LookupError):
            fetch_task_by_id(connection, 999)
    finally:
        connection.close()


class _FakeValidationError:
    def errors(self) -> list[dict[str, object]]:
        return [{"loc": (), "type": "unknown"}]


def test_format_validation_error_falls_back_to_generic_message() -> None:
    assert format_validation_error(_FakeValidationError()) == "Request body is invalid."
