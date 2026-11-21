# 06 - Testing & QA

Cours : <https://courses.dallard.tech/ci_cd/testing_python_intro/>

| Fichier | Rôle |
|---|---|
| [`app.py`](app.py) | domain layer (fonctions pures) + service layer (`ProductRepository`, `OrderService`) + `ShoppingCart` de l'exemple AAA |
| [`groq_chat.py`](groq_chat.py) | `ask_groq()` avec client injectable |
| [`../tests/test_app.py`](../tests/test_app.py) | tests **unitaires** (discount, tax, total, cart en AAA) |
| [`../tests/test_integration_app.py`](../tests/test_integration_app.py) | tests **d'intégration** `OrderService` + `ProductRepository` |
| [`../tests/test_groq_chat.py`](../tests/test_groq_chat.py) | **mocking** avec `pytest-mock` : réponse simulée, vérification de l'appel, panne d'API simulée |
| [`../tests/conftest.py`](../tests/conftest.py) | fixtures partagées |

Notions mises en pratique :

- **pyramide des tests** : beaucoup d'unitaires, quelques tests d'intégration
- **fixtures** (`@pytest.fixture`) et partage via `conftest.py`
- **mocking** : on teste que *notre code* envoie la bonne requête, pas que le LLM répond juste
- **markers** : `@pytest.mark.slow` (test réel vers l'API, ignoré par défaut) — déclarés dans `pyproject.toml`
- **coverage** : `pytest --cov`
- **AAA** (Arrange-Act-Assert)
- **tox** : [`../tox.ini`](../tox.ini) pour tester sur plusieurs versions de Python

```bash
pytest                       # tous les tests (sauf slow)
pytest -m slow               # test réel Groq (nécessite GROQ_API_KEY + pip install groq)
pytest --cov --cov-report=term-missing
tox                          # py311 + py312
```
