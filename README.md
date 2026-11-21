# OOP & Design patterns in Python - exercices (AIDAMS 2A)

Solutions des exercices pratiques du cours *Object Oriented Programming &
Design pattern in Python* (B. Dallard, CentraleSupélec).
Ressources du cours : <https://courses.dallard.tech/>

| # | Partie du cours | Exercice | Dossier |
|---|---|---|---|
| 1 | Linux & shell | Configurer un environnement de dev (`env_install.sh`) | [`01_linux_bash`](01_linux_bash) |
| 2 | GitHub | Git mini exo (commandes + réponses + `install.sh`) | [`02_git`](02_git) |
| 3 | OOP | Operator overloading & inheritance | [`03_oop`](03_oop) |
| 4 | UML | Hospital Management System & ABCD Records (diagrammes + code) | [`04_uml`](04_uml) |
| 5 | Design patterns | Factory, Builder, Singleton, Adapter, Decorator, Strategy, Template Method | [`05_design_patterns`](05_design_patterns) |
| 6 | Testing & QA | Tests unitaires, intégration, mocking (Groq), fixtures, markers, coverage | [`06_testing`](06_testing) + [`tests`](tests) |

## Lancer le projet

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest                                   # toute la suite de tests
pytest --cov --cov-report=term-missing   # avec la couverture
python 05_design_patterns/structural/decorator.py   # lancer un exercice
```

Les diagrammes UML sont écrits en Mermaid et s'affichent directement sur GitHub.

## Structure

```
.
├── 01_linux_bash/        env_install.sh + réponses
├── 02_git/               réponses au Git mini exo + install.sh
├── 03_oop/               operator_overloading.py, inheritance.py
├── 04_uml/               *_uml.md (diagrammes) + hospital.py, abcd_records.py
├── 05_design_patterns/
│   ├── creational/       factory.py, builder.py, singleton.py (+ config.json)
│   ├── structural/       adapter.py, decorator.py
│   └── behavioral/       strategy.py, template_method.py
├── 06_testing/           app.py, groq_chat.py
├── tests/                conftest.py + un fichier de tests par partie
├── pyproject.toml        config pytest / coverage
├── tox.ini               tests multi-versions (py311, py312)
└── requirements.txt
```
