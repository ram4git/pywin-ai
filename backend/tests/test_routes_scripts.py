# win-auto/backend/tests/test_routes_scripts.py
import pytest
from fastapi.testclient import TestClient
from main import app
from db.database import Base, engine


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


class TestScriptsRoutes:
    def test_create_script(self):
        resp = client.post("/api/scripts", json={"name": "Test", "prompt": "Open notepad"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Test"
        assert "id" in resp.json()

    def test_list_scripts(self):
        client.post("/api/scripts", json={"name": "S1", "prompt": "p1"})
        client.post("/api/scripts", json={"name": "S2", "prompt": "p2"})
        resp = client.get("/api/scripts")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_script(self):
        sid = client.post("/api/scripts", json={"name": "S1", "prompt": "p1"}).json()["id"]
        resp = client.get(f"/api/scripts/{sid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "S1"

    def test_delete_script(self):
        sid = client.post("/api/scripts", json={"name": "S1", "prompt": "p1"}).json()["id"]
        assert client.delete(f"/api/scripts/{sid}").status_code == 204
        assert client.get(f"/api/scripts/{sid}").status_code == 404
