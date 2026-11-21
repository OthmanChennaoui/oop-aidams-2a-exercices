"""REST API with FastAPI on top of the e-commerce use case (slide 40).

What it shows:
  - route registration decorators: @app.get / @app.post map URLs to functions
  - dependency injection with Depends(): the repository, the order service and
    the LLM client are injected, so the tests can replace them
    (app.dependency_overrides) without touching the routes

Run it:  uvicorn api:app --reload --app-dir 06_testing
Docs:    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app import OrderService, ProductRepository
from groq_chat import ask_groq

app = FastAPI(title="Shop API", version="1.0.0")


# ------------------------------------------------------------ schemas ---
class OrderRequest(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


# ------------------------------------------------------- dependencies ---
@lru_cache(maxsize=1)
def get_repository() -> ProductRepository:
    """One shared in-memory "database" for the whole app."""
    return ProductRepository()


def get_order_service(repo: ProductRepository = Depends(get_repository)) -> OrderService:
    return OrderService(repo)


def get_llm_client() -> Any:
    """Real Groq client, created only when /chat is called (needs GROQ_API_KEY)."""
    from groq import Groq

    return Groq()


# ------------------------------------------------------------- routes ---
@app.get("/status")
def get_status() -> dict:
    return {"status": "ok"}


@app.get("/products/{sku}")
def get_product(sku: str, repo: ProductRepository = Depends(get_repository)) -> dict:
    product = repo.get_product(sku)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    return {"sku": sku, **product}


@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: OrderRequest, service: OrderService = Depends(get_order_service)) -> dict:
    result = service.place_order(order.sku, order.quantity)
    if not result["success"]:
        code = status.HTTP_404_NOT_FOUND if result["error"] == "Product not found" else status.HTTP_409_CONFLICT
        raise HTTPException(code, result["error"])
    return result


@app.post("/chat")
def chat(request: ChatRequest, client: Any = Depends(get_llm_client)) -> dict:
    try:
        answer = ask_groq(request.question, client=client)
    except ValueError as exc:  # blank question ("   ")
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:  # the LLM provider is down, rate-limited...
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "LLM service unavailable") from exc
    return {"question": request.question, "answer": answer}
