def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_and_me(client, auth):
    r = client.get("/auth/me", headers=auth)
    assert r.status_code == 200
    assert r.json()["username"] == "alice"
    assert "hashed_password" not in r.json()


def test_register_duplicate(client, auth):
    r = client.post("/auth/register", json={"username": "alice", "password": "another123"})
    assert r.status_code == 409


def test_register_validation(client):
    too_short_name = {"username": "ab", "password": "secret123"}
    too_short_password = {"username": "bob", "password": "short"}
    assert client.post("/auth/register", json=too_short_name).status_code == 422
    assert client.post("/auth/register", json=too_short_password).status_code == 422


def test_login_wrong_password(client, auth):
    r = client.post("/auth/login", data={"username": "alice", "password": "wrongpass"})
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post("/auth/login", data={"username": "nobody", "password": "secret123"})
    assert r.status_code == 401


def test_protected_without_token(client):
    assert client.get("/todos").status_code == 401
    assert client.get("/auth/me").status_code == 401


def test_protected_with_bad_token(client):
    r = client.get("/todos", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401
