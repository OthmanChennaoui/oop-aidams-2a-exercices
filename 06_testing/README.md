# 06 - Testing & QA

Course: <https://courses.dallard.tech/ci_cd/testing_python_intro/> (slides 89-93)

| File | Role |
|---|---|
| [`app.py`](app.py) | domain layer (pure functions) + service layer (`ProductRepository`, `OrderService`) + `ShoppingCart` from the AAA example |
| [`groq_chat.py`](groq_chat.py) | `ask_groq()` with an injectable client |
| [`api.py`](api.py) | **FastAPI** REST API (slide 40): `@app.get` / `@app.post` routes, `Depends()` injection of the repository, the order service and the LLM client |
| [`../tests/test_app.py`](../tests/test_app.py) | **unit** tests (discount, tax, total, cart in AAA style) |
| [`../tests/test_integration_app.py`](../tests/test_integration_app.py) | **integration** tests for `OrderService` + `ProductRepository` |
| [`../tests/test_groq_chat.py`](../tests/test_groq_chat.py) | **mocking** with `pytest-mock`: fake response, checking the call, simulated API failure |
| [`../tests/test_api.py`](../tests/test_api.py) | **API** tests with `TestClient` + `app.dependency_overrides` (fresh repository per test, mocked Groq client, 404 / 409 / 422 / 503 cases) |
| [`../tests/conftest.py`](../tests/conftest.py) | shared fixtures |

Concepts put into practice:

- **test pyramid**: many unit tests, a few integration tests
- **fixtures** (`@pytest.fixture`) shared through `conftest.py`
- **mocking**: we test that *our code* sends the right request, not that the LLM answers correctly
- **markers**: `@pytest.mark.slow` (real API test, skipped by default), declared in `pyproject.toml`
- **coverage**: `pytest --cov`
- **AAA** (Arrange-Act-Assert)
- **tox**: [`../tox.ini`](../tox.ini) to test against several Python versions

```bash
pytest                       # all tests (except slow)
pytest -m slow               # real Groq test (needs GROQ_API_KEY + pip install groq)
pytest --cov --cov-report=term-missing
tox                          # py311 + py312
```

Run the API locally:

```bash
uvicorn api:app --reload --app-dir 06_testing   # then open http://127.0.0.1:8000/docs
```
