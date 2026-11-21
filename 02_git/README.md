# 02 - Git mini exo

Énoncé : <https://gist.github.com/bdallard/8bdbdd70f234f94823c0c2cde9515388>

## Part 1 - Setup & config

```bash
git --version
git config --global user.name "Prénom Nom"
git config --global user.email "moi@example.com"
git config --global init.defaultBranch main
git config --list          # vérifier
```

## Part 2 - Create your first repository

```bash
mkdir my-first-repo
cd my-first-repo
git init
touch readme.txt
```

## Part 3 - Your first commit

| Question | Commande |
|---|---|
| État du dépôt | `git status` |
| Stager `readme.txt` | `git add readme.txt` |
| Committer | `git commit -m "Add readme file"` |
| Historique | `git log` |

## Part 4 - Make changes

```bash
echo "Hello Git" >> readme.txt
git status
```

`git status` indique que `readme.txt` est **modifié mais non stagé**
(« Changes not staged for commit ») : Git voit que le fichier diffère du
dernier commit, mais la modification n'ira dans le prochain commit qu'après
un `git add`.

```bash
git add readme.txt
git commit -m "Add greeting line to readme"
git log --oneline   # -> 2 commits
```

## Part 5 - Exploration

- `git diff` : montre les lignes modifiées dans le working directory qui ne
  sont pas encore stagées (`git diff --staged` pour ce qui est stagé).
- `git log --oneline` : historique compact, une ligne par commit
  (hash court + message).

## Part 6 - Working with branches

| Question | Commande |
|---|---|
| Lister les branches | `git branch` (`git branch -a` pour inclure les distantes) |
| Créer `feature-script` | `git branch feature-script` |
| Basculer dessus | `git switch feature-script` (ou `git checkout feature-script`) |
| Créer + basculer sur `dev` | `git switch -c dev` (ou `git checkout -b dev`) |
| Revenir sur `feature-script` | `git switch feature-script` |
| Vérifier la branche courante | `git branch --show-current` (ou `git status`) |

## Part 7 - Create a bash script on a branch

Le script est [`install.sh`](install.sh).

```bash
git switch feature-script
touch install.sh            # puis écrire le contenu
chmod +x install.sh
git add install.sh
git commit -m "Add install script"
git log --oneline
```

## Part 8 - Merge branches

```bash
git switch main
ls
```

`install.sh` **n'est pas présent** : il a été committé uniquement sur
`feature-script`. Le working directory reflète la branche courante.

```bash
git merge feature-script
ls                     # install.sh apparaît
git log --oneline      # le commit "Add install script" est maintenant dans main
git branch -d feature-script
```

Comme `main` n'avait pas bougé, Git fait un **fast-forward** : il avance
simplement le pointeur `main` sur le commit de `feature-script`, sans commit
de merge.

## Part 9 - Push to GitHub

Créer `my-first-repo` sur github.com **sans README**, puis :

```bash
git remote add origin https://github.com/<user>/my-first-repo.git
git push -u origin main
```

Après rafraîchissement, la page GitHub montre les fichiers (`readme.txt`,
`install.sh`) et l'historique des commits.

## Part 10 - Delete and clone

```bash
cd ..
rm -rf my-first-repo
git clone https://github.com/<user>/my-first-repo.git
cd my-first-repo && ls
```

## Part 11 - Full workflow practice

```bash
rm -rf my-first-repo                     # + supprimer le repo sur GitHub (Settings > Delete)
mkdir bash-installer && cd bash-installer
git init
echo "# bash-installer" > README.md
echo "Script d'installation automatique de paquets." >> README.md
git add README.md && git commit -m "Add README"
git switch -c feature-install
cp ../install.sh . && chmod +x install.sh
git add install.sh && git commit -m "Add install script"
git switch main
git merge feature-install
git branch -d feature-install
git remote add origin https://github.com/<user>/bash-installer.git
git push -u origin main
```

## Reflection questions

1. **Pourquoi le contrôle de version ?** Historique complet, retour arrière
   possible, travail en équipe sans écraser le travail des autres, sauvegarde
   distante.
2. **Staging vs commit ?** Le *staging* (`git add`) prépare une sélection de
   modifications ; le *commit* enregistre définitivement ce snapshot dans
   l'historique. Le staging permet de faire des commits ciblés.
3. **Quand committer ?** Dès qu'une unité logique de travail est terminée et
   fonctionne : petit et souvent.
4. **`git init` vs `git clone` ?** `init` crée un nouveau dépôt vide en local ;
   `clone` copie un dépôt existant (historique compris) et configure le remote
   `origin`.
5. **Pourquoi de bons messages ?** Pour comprendre plus tard *pourquoi* un
   changement a été fait, retrouver l'origine d'un bug, faciliter la revue.
6. **À quoi servent les branches ?** Isoler un développement (feature, fix)
   sans casser `main`, travailler en parallèle, expérimenter.
7. **Quand créer une branche ?** Pour toute nouvelle fonctionnalité, correction
   ou expérimentation ; `main` doit rester stable et déployable.
