# 01 - Bash script exercise

Exercise: <https://courses.dallard.tech/linux/bash_exo/> (slide 18)

## Part 1 - Improve your shell experience

| Question | Command / answer |
|---|---|
| Show the user's default shell | `dscl . -read ~/ UserShell` (macOS) or `getent passwd "$USER" \| cut -d: -f7` (Linux) |
| Check the `SHELL` variable | `echo $SHELL` |
| Shell actually running | `echo $0` or `ps -p $$` |
| Install Oh My Zsh | `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"` |
| Install Oh My Bash | `bash -c "$(curl -fsSL https://raw.githubusercontent.com/ohmybash/oh-my-bash/master/tools/install.sh)"` |
| Pick a theme | in `~/.zshrc`: `ZSH_THEME="agnoster"` |

**What is the `source` command for?** `source file` (or `. file`) runs the file
*in the current shell* instead of a subshell. The variables, aliases and
functions it defines therefore stay available. It is used to reload the
configuration after editing it: `source ~/.zshrc`.

### Step 1.3 - Git plugin

In `~/.zshrc` (or `~/.bashrc`):

```bash
plugins=(git)
```

then `source ~/.zshrc`. Check: `gst` = `git status`, `gl` = `git pull`,
`gp` = `git push`, `glog` = `git log --oneline --decorate --graph`.

## Part 2 - Check your Python installation

```bash
python3 --version
```

## Part 3 & 4 - Script

The script is [`env_install.sh`](env_install.sh).

```bash
chmod +x env_install.sh
./env_install.sh --dry-run    # see what would be done
./env_install.sh              # actually install
./env_install.sh --uninstall  # undo
```

It implements the 6 required features and every bonus: ANSI colors,
timestamped log (`~/env_install.log`), strict mode (`set -euo pipefail`),
`--dry-run` / `--verbose` / `--quiet` / `--uninstall` options.

### Verification checklist

- [x] the prompt shows the framework's theme
- [x] `gst` behaves like `git status`
- [x] `python3 --version` → 3.x
- [x] `python3 -m pip --version` → pip version
- [x] `jupyter notebook` starts
- [x] macOS: `brew doctor` reports no serious issue
