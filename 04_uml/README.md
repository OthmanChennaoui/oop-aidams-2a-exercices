# 04 - UML practice

Énoncé : <https://gist.github.com/bdallard/2d2407c4de4c182afca6d3ec7235e9eb>

Les diagrammes sont écrits en [Mermaid](https://mermaid.js.org/) : GitHub les
affiche directement comme des images dans les fichiers `.md`.

| Exercice | Diagrammes | Code |
|---|---|---|
| Exo 1 - Hospital Management System | [`hospital_uml.md`](hospital_uml.md) : classes (Task 1, 2, 3), séquence, 3 SSD, réponses aux questions | [`hospital.py`](hospital.py) |
| Exo 2 - ABCD Records | [`abcd_records_uml.md`](abcd_records_uml.md) : use cases (L1, L2), classes (L1, L2), diagramme d'objets du scénario, 4 séquences (L3) | [`abcd_records.py`](abcd_records.py) |

```bash
python 04_uml/hospital.py
python 04_uml/abcd_records.py
pytest tests/test_uml.py
```
