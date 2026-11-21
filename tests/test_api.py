"""API tests with FastAPI's TestClient.

The dependencies are replaced through app.dependency_overrides:
  - a fresh ProductRepository per test (no shared state between tests)
  - a mocked Groq client (no network, no API key, no cost)
"""

import pytest
from fastapi.testclient import TestClient

from api import app, get_llm_client, get_repository
from app import ProductRepository


@pytest.fixture
def repo():
    return ProductRepository()


@pytest.fixture
def client(repo, fake_groq_client):
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_llm_client] = lambda: fake_groq_client
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class TestProducts:
    def test_get_existing_product(self, client):
        response = client.get("/products/MUG")
        assert response.status_code == 200
        assert response.json() == {"sku": "MUG", "name": "Coffee Mug", "price": 12.0, "stock": 100}

    def test_unknown_product_is_404(self, client):
        assert client.get("/products/PANTS").status_code == 404


class TestOrders:
    def test_create_order(self, client, repo):
        response = client.post("/orders", json={"sku": "SHIRT", "quantity": 2})

        assert response.status_code == 201
        assert response.json() == {"success": True, "item": "T-Shirt", "quantity": 2, "total": 60.0}
        assert repo.get_product("SHIRT")["stock"] == 48

    def test_unknown_product_is_404(self, client):
        response = client.post("/orders", json={"sku": "PANTS", "quantity": 1})
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_not_enough_stock_is_409(self, client, repo):
        response = client.post("/orders", json={"sku": "HAT", "quantity": 999})
        assert response.status_code == 409
        assert repo.get_product("HAT")["stock"] == 30

    @pytest.mark.parametrize("payload", [{"sku": "HAT", "quantity": 0}, {"sku": "HAT"}, {"sku": "", "quantity": 1}])
    def test_invalid_body_is_422(self, client, payload):
        assert client.post("/orders", json=payload).status_code == 422

    def test_each_test_gets_a_fresh_repository(self, client, repo):
        assert repo.get_product("SHIRT")["stock"] == 50


class TestChat:
    def test_chat_returns_mocked_answer(self, client, fake_groq_client):
        response = client.post("/chat", json={"question": "What is 2+2?"})

        assert response.status_code == 200
        assert response.json() == {"question": "What is 2+2?", "answer": "4"}
        fake_groq_client.chat.completions.create.assert_called_once()

    @pytest.mark.parametrize("question", ["", "   "])
    def test_empty_question_is_422(self, client, fake_groq_client, question):
        assert client.post("/chat", json={"question": question}).status_code == 422
        fake_groq_client.chat.completions.create.assert_not_called()

    def test_provider_down_is_503(self, client, fake_groq_client):
        fake_groq_client.chat.completions.create.side_effect = Exception("API down")

        response = client.post("/chat", json={"question": "Hello?"})

        assert response.status_code == 503
        assert response.json()["detail"] == "LLM service unavailable"
