def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_todo(client):
    response = client.post("/todos/", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["completed"] is False
    assert "id" in data


def test_list_todos(client):
    client.post("/todos/", json={"title": "Task 1"})
    client.post("/todos/", json={"title": "Task 2"})
    response = client.get("/todos/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_todo(client):
    created = client.post("/todos/", json={"title": "Read a book"}).json()
    response = client.get(f"/todos/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Read a book"


def test_get_todo_not_found(client):
    response = client.get("/todos/999")
    assert response.status_code == 404


def test_update_todo(client):
    created = client.post("/todos/", json={"title": "Old title"}).json()
    response = client.patch(f"/todos/{created['id']}", json={"title": "New title", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["completed"] is True


def test_delete_todo(client):
    created = client.post("/todos/", json={"title": "To delete"}).json()
    response = client.delete(f"/todos/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/todos/{created['id']}").status_code == 404
