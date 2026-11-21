# OOP & Design patterns in Python - exercises (AIDAMS 2A)

Solutions to the practical exercises of the *Object Oriented Programming &
Design pattern in Python* course (B. Dallard, CentraleSupélec).
Course resources: <https://courses.dallard.tech/>

| # | Course part | Exercise | Folder |
|---|---|---|---|
| 1 | Linux & shell | Set up a development environment (`env_install.sh`) | [`01_linux_bash`](01_linux_bash) |
| 2 | GitHub | Git mini exo (commands + answers + `install.sh`) | [`02_git`](02_git) |
| 3 | OOP | Operator overloading & inheritance | [`03_oop`](03_oop) |
| 4 | UML | Hospital Management System & ABCD Records (diagrams + code) | [`04_uml`](04_uml) |
| 5 | Design patterns | Factory, Builder, Singleton, Adapter, Decorator, Strategy, Template Method | [`05_design_patterns`](05_design_patterns) |
| 6 | Testing & QA | Unit tests, integration tests, mocking (Groq), fixtures, markers, coverage | [`06_testing`](06_testing) + [`tests`](tests) |

## Running the project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

pytest                                   # whole test suite
pytest --cov --cov-report=term-missing   # with coverage
python 05_design_patterns/structural/decorator.py   # run one exercise
```

The UML diagrams are written in Mermaid and are rendered directly by GitHub.

## Structure

```
.
├── 01_linux_bash/        env_install.sh + answers
├── 02_git/               Git mini exo answers + install.sh
├── 03_oop/               operator_overloading.py, inheritance.py
├── 04_uml/               *_uml.md (diagrams) + hospital.py, abcd_records.py
├── 05_design_patterns/
│   ├── creational/       factory.py, builder.py, singleton.py (+ config.json)
│   ├── structural/       adapter.py, decorator.py
│   └── behavioral/       strategy.py, template_method.py
├── 06_testing/           app.py, groq_chat.py
├── tests/                conftest.py + one test file per part
├── pyproject.toml        pytest / coverage config
├── tox.ini               multi-version testing (py311, py312)
└── requirements.txt
```
