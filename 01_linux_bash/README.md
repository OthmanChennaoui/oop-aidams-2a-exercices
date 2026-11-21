# 01 - Bash script exercise

Énoncé : <https://courses.dallard.tech/linux/bash_exo/>

## Part 1 - Improve your shell experience

| Question | Commande / réponse |
|---|---|
| Afficher le shell par défaut de l'utilisateur | `dscl . -read ~/ UserShell` (macOS) ou `getent passwd "$USER" \| cut -d: -f7` (Linux) |
| Vérifier la variable `SHELL` | `echo $SHELL` |
| Shell réellement en cours | `echo $0` ou `ps -p $$` |
| Installer Oh My Zsh | `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"` |
| Installer Oh My Bash | `bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"` |
| Choisir un thème | dans `~/.zshrc` : `ZSH_THEME="agnoster"` |

**À quoi sert `source` ?** `source fichier` (ou `. fichier`) exécute le fichier
*dans le shell courant* au lieu d'un sous-shell. Les variables, alias et
fonctions qu'il définit restent donc disponibles. On l'utilise pour recharger
la config après modification : `source ~/.zshrc`.

### Step 1.3 - Plugin git

Dans `~/.zshrc` (ou `~/.bashrc`) :

```bash
plugins=(git)
```

puis `source ~/.zshrc`. Vérification : `gst` = `git status`, `gl` = `git pull`,
`gp` = `git push`, `glog` = `git log --oneline --decorate --graph`.

## Part 2 - Check your Python installation

```bash
python3 --version
```

## Part 3 & 4 - Script

Le script est [`env_install.sh`](env_install.sh).

```bash
chmod +x env_install.sh
./env_install.sh --dry-run    # voir ce qui serait fait
./env_install.sh              # installer pour de vrai
./env_install.sh --uninstall  # annuler
```

Il implémente les 6 features demandées et tous les bonus : couleurs ANSI,
log horodaté (`~/env_install.log`), strict mode (`set -euo pipefail`), options
`--dry-run` / `--verbose` / `--quiet` / `--uninstall`.

### Checklist de vérification

- [x] le prompt affiche le thème du framework
- [x] `gst` répond comme `git status`
- [x] `python3 --version` → 3.x
- [x] `python3 -m pip --version` → version de pip
- [x] `jupyter notebook` se lance
- [x] macOS : `brew doctor` sans erreur grave
