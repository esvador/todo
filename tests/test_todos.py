def create(client, auth, **kwargs):
    payload = {"title": "Buy milk", **kwargs}
    r = client.post("/todos", json=payload, headers=auth)
    assert r.status_code == 201, r.text
    return r.json()


def test_create_and_get(client, auth):
    todo = create(client, auth, description="2 liters")
    assert todo["title"] == "Buy milk"
    assert todo["is_done"] is False

    r = client.get(f"/todos/{todo['id']}", headers=auth)
    assert r.status_code == 200
    assert r.json()["description"] == "2 liters"


def test_create_empty_title(client, auth):
    assert client.post("/todos", json={"title": ""}, headers=auth).status_code == 422


def test_list_filter_search_pagination(client, auth):
    create(client, auth, title="Buy milk")
    done = create(client, auth, title="Write code")
    create(client, auth, title="Buy bread")
    client.patch(f"/todos/{done['id']}", json={"is_done": True}, headers=auth)

    assert len(client.get("/todos", headers=auth).json()) == 3
    assert [t["title"] for t in client.get("/todos?is_done=true", headers=auth).json()] == ["Write code"]
    assert len(client.get("/todos?is_done=false", headers=auth).json()) == 2
    assert len(client.get("/todos?q=buy", headers=auth).json()) == 2
    assert len(client.get("/todos?limit=2", headers=auth).json()) == 2
    assert len(client.get("/todos?limit=2&offset=2", headers=auth).json()) == 1


def test_update_partial(client, auth):
    todo = create(client, auth)
    r = client.patch(f"/todos/{todo['id']}", json={"is_done": True}, headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["is_done"] is True
    assert body["title"] == "Buy milk"


def test_update_null_title_rejected(client, auth):
    todo = create(client, auth)
    r = client.patch(f"/todos/{todo['id']}", json={"title": None}, headers=auth)
    assert r.status_code == 422


def test_delete(client, auth):
    todo = create(client, auth)
    assert client.delete(f"/todos/{todo['id']}", headers=auth).status_code == 204
    assert client.get(f"/todos/{todo['id']}", headers=auth).status_code == 404


def test_not_found(client, auth):
    assert client.get("/todos/999", headers=auth).status_code == 404
    assert client.patch("/todos/999", json={"is_done": True}, headers=auth).status_code == 404
    assert client.delete("/todos/999", headers=auth).status_code == 404


def test_users_isolated(client, make_user):
    alice = make_user("alice")
    bob = make_user("bob")
    todo = create(client, alice)

    assert client.get("/todos", headers=bob).json() == []
    assert client.get(f"/todos/{todo['id']}", headers=bob).status_code == 404
    assert client.patch(f"/todos/{todo['id']}", json={"title": "x"}, headers=bob).status_code == 404
    assert client.delete(f"/todos/{todo['id']}", headers=bob).status_code == 404
    assert client.get(f"/todos/{todo['id']}", headers=alice).status_code == 200
