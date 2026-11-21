# 03 - OOP Problems

Énoncé : <https://gist.github.com/bdallard/b2f2c910e3a9b564a30c86991c97b4fc>

| Fichier | Contenu |
|---|---|
| [`operator_overloading.py`](operator_overloading.py) | `Complex` (+, -), `Person` (>), `Vector` (* = produit scalaire), `Circle` (les 6 comparaisons), `Point` (comparaison par distance à l'origine), `Matrix` (produit matriciel) |
| [`inheritance.py`](inheritance.py) | `Vehicle`/`Car`/`Bicycle`, `Person`/`Student`/`Employee`, `BankAccount`/`SavingsAccount` (avec `transfer`) |

Le gist n'a pas de *Problem 3* dans la partie Operator Overloading (il passe de 2 à 4).

```bash
python 03_oop/operator_overloading.py
python 03_oop/inheritance.py
pytest tests/test_oop.py
```

## Points à retenir

- Les opérateurs Python appellent des *dunder methods* : `a + b` → `a.__add__(b)`,
  `a > b` → `a.__gt__(b)`, `a * b` → `a.__mul__(b)`.
- Renvoyer `NotImplemented` (et non `False`) dans `__eq__` quand l'autre objet
  n'est pas du bon type : Python essaie alors l'opération inverse.
- Définir `__eq__` rend la classe non *hashable* : il faut redéfinir `__hash__`
  si on veut la mettre dans un `set` / comme clé de `dict`.
- `@functools.total_ordering` génère `<=`, `>`, `>=` à partir de `__eq__` + `__lt__`
  (utilisé pour `Point`, écrit à la main pour `Circle`).
- `super().__init__(...)` réutilise le constructeur du parent ; `super().introduce()`
  étend une méthode au lieu de la recopier.
