"""Singleton - refactoring du gestionnaire de configuration.

Problèmes du code legacy :
  - config.json est relu à chaque appel (I/O inutile)
  - pas d'état partagé : chaque module a sa propre copie
  - une modification dans un module n'est pas vue par les autres
  - difficile à mocker : pas de point d'entrée unique

Solution : ConfigManager charge le fichier une seule fois et renvoie toujours
la même instance via get_instance(). get("a.b") lit les valeurs imbriquées.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.json")
_MISSING = object()


class ConfigManager:
    _instance: ConfigManager | None = None
    _lock = threading.Lock()

    def __init__(self, path: Path | str = DEFAULT_CONFIG_PATH) -> None:
        # On interdit l'instanciation directe pour garantir l'unicité.
        if ConfigManager._instance is not None:
            raise RuntimeError("Use ConfigManager.get_instance()")
        self.path = Path(path)
        self.load_count = 0
        self._data: dict = {}
        self._load()

    @classmethod
    def get_instance(cls, path: Path | str = DEFAULT_CONFIG_PATH) -> ConfigManager:
        # Double-checked locking : thread-safe sans verrouiller à chaque appel.
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(path)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Utile pour les tests : oublie l'instance courante."""
        cls._instance = None

    def _load(self) -> None:
        with self.path.open(encoding="utf-8") as f:
            self._data = json.load(f)
        self.load_count += 1

    def get(self, key: str, default: Any = _MISSING) -> Any:
        """Accès par chemin pointé : get("database.host")."""
        node: Any = self._data
        for part in key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            elif default is not _MISSING:
                return default
            else:
                raise KeyError(key)
        return node

    def set(self, key: str, value: Any) -> None:
        """Modifie une valeur : tous les modules la voient (état partagé)."""
        *parents, last = key.split(".")
        node = self._data
        for part in parents:
            node = node.setdefault(part, {})
        node[last] = value


# ----- Le code applicatif refactoré : plus aucun load_config() -----------
def start_application() -> str:
    config = ConfigManager.get_instance()
    return f"Starting {config.get('app.name')} (debug={config.get('app.debug')})"


def connect_database() -> str:
    config = ConfigManager.get_instance()
    return f"Connecting to database at {config.get('database.host')}:{config.get('database.port')}"


def send_email(to: str, subject: str) -> str:
    config = ConfigManager.get_instance()
    return f"Sending '{subject}' to {to} from {config.get('email.sender')} via {config.get('email.smtp_host')}"


def process_payment(amount: float) -> str:
    config = ConfigManager.get_instance()
    return f"Processing {amount}€ in {config.get('payment.environment')} mode"


if __name__ == "__main__":
    print(start_application())
    print(connect_database())
    print(send_email("user@test.com", "Welcome"))
    print(process_payment(99.99))
    config = ConfigManager.get_instance()
    print("same instance:", config is ConfigManager.get_instance(), "| file loaded", config.load_count, "time(s)")
