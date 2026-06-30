import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

import pytest
import app as flask_app

@pytest.fixture
def client(tmp_path):
    flask_app.app.config["TESTING"] = True
    flask_app.DB_PATH = str(tmp_path / "test.db")
    flask_app.SCHEMA_PATH = str(
        os.path.join(os.path.dirname(__file__), '..', 'db', 'schema.sql')
    )
    with flask_app.app.app_context():
        flask_app.init_db()
    with flask_app.app.test_client() as c:
        yield c

def test_session_not_found(client):
    r = client.get("/session/60123456789")
    assert r.status_code == 200
    assert r.json == {}

def test_upsert_and_get_session(client):
    client.post("/session", json={"phone_number": "60123456789"})
    r = client.get("/session/60123456789")
    assert r.status_code == 200
    assert r.json["phone_number"] == "60123456789"

def test_delete_session(client):
    client.post("/session", json={"phone_number": "60111111111"})
    client.delete("/session/60111111111")
    r = client.get("/session/60111111111")
    assert r.status_code == 200
    assert r.json == {}

def test_create_order_generates_ticket(client):
    r = client.post("/orders", json={
        "phone_number": "60123456789",
        "customer_name": "John",
        "service": "ATS 優化",
        "amount": 5,
        "details": "test"
    })
    assert r.status_code == 200
    assert r.json["ticket_no"].startswith("RES-")

def test_ticket_format(client):
    r = client.post("/orders", json={
        "phone_number": "60123456789",
        "customer_name": "Jane",
        "service": "求職信",
        "amount": 3,
        "details": "test"
    })
    ticket = r.json["ticket_no"]
    assert len(ticket) == 17  # RES-YYYYMMDD-XXXX = 17 chars

def test_get_order_by_ticket(client):
    r = client.post("/orders", json={
        "phone_number": "60123456789",
        "customer_name": "Bob",
        "service": "求職信",
        "amount": 3,
        "details": "test"
    })
    ticket = r.json["ticket_no"]
    r2 = client.get(f"/orders/ticket/{ticket}")
    assert r2.status_code == 200
    assert r2.json["service"] == "求職信"

def test_update_order_status(client):
    r = client.post("/orders", json={
        "phone_number": "60123456789",
        "customer_name": "Alice",
        "service": "從零寫",
        "amount": 7,
        "details": "test"
    })
    ticket = r.json["ticket_no"]
    client.post(f"/orders/ticket/{ticket}/status", json={"status": "confirmed"})
    r2 = client.get(f"/orders/ticket/{ticket}")
    assert r2.json["status"] == "confirmed"

def test_add_and_get_conversation(client):
    client.post("/conversations", json={
        "phone_number": "60123456789",
        "role": "user",
        "content": "hello"
    })
    r = client.get("/conversations/60123456789")
    assert len(r.json["history"]) == 1
    assert r.json["history"][0]["content"] == "hello"

def test_ticket_sequential_per_day(client):
    r1 = client.post("/orders", json={"phone_number": "A", "customer_name": "X", "service": "S", "amount": 5, "details": ""})
    r2 = client.post("/orders", json={"phone_number": "B", "customer_name": "Y", "service": "S", "amount": 5, "details": ""})
    n1 = int(r1.json["ticket_no"].split("-")[2])
    n2 = int(r2.json["ticket_no"].split("-")[2])
    assert n2 == n1 + 1
