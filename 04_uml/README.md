# 04 - UML practice

Exercise: <https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb>

The diagrams are written in [Mermaid](https://mermaid.js.org/): GitHub renders
them as images directly inside the `.md` files.

| Exercise | Diagrams | Code |
|---|---|---|
| Exo 1 - Hospital Management System | [`hospital_uml.md`](hospital_uml.md): class diagrams (Tasks 1, 2, 3), sequence diagram, 3 SSDs, answers to the questions | [`hospital.py`](hospital.py) |
| Exo 2 - ABCD Records | [`abcd_records_uml.md`](abcd_records_uml.md): use case diagrams (L1, L2), class diagrams (L1, L2), object diagram of the scenario, 4 sequence diagrams (L3) | [`abcd_records.py`](abcd_records.py) |

```bash
python 04_uml/hospital.py
python 04_uml/abcd_records.py
pytest tests/test_uml.py
```
