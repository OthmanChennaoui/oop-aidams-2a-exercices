"""Fixtures shared by every test file."""

import pytest

from app import OrderService, ProductRepository
from singleton import ConfigManager
import template_method


@pytest.fixture
def order_service():
    """Fresh repo + service for each test."""
    return OrderService(ProductRepository())


@pytest.fixture
def report_data():
    return [
        {"name": "Sales Q1", "value": 15000},
        {"name": "Sales Q2", "value": 18000},
    ]


@pytest.fixture
def fresh_config():
    """Each test starts from a fresh Singleton."""
    ConfigManager.reset()
    yield ConfigManager.get_instance()
    ConfigManager.reset()


@pytest.fixture(autouse=True)
def no_pipeline_delay(monkeypatch):
    """The ETL pipelines simulate latency: useless in tests."""
    monkeypatch.setattr(template_method.DataPipeline, "io_delay", 0)


@pytest.fixture
def fake_groq_client(mocker):
    """Fake Groq client whose response has the same shape as the real one."""
    mock_choice = mocker.Mock()
    mock_choice.message.content = "4"
    mock_response = mocker.Mock()
    mock_response.choices = [mock_choice]
    client = mocker.Mock()
    client.chat.completions.create.return_value = mock_response
    return client
