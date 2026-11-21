# 02 - Git mini exo

Exercise: <https://gist.github.com/bdallard/8bdbdd70f234f94823c0c2cde9515388>

## Part 1 - Setup & config

```bash
git --version
git config --global user.name "First Last"
git config --global user.email "me@example.com"
git config --global init.defaultBranch main
git config --list          # check
```

## Part 2 - Create your first repository

```bash
mkdir my-first-repo
cd my-first-repo
git init
touch readme.txt
```

## Part 3 - Your first commit

| Question | Command |
|---|---|
| Repository state | `git status` |
| Stage `readme.txt` | `git add readme.txt` |
| Commit | `git commit -m "Add readme file"` |
| History | `git log` |

## Part 4 - Make changes

```bash
echo "Hello Git" >> readme.txt
git status
```

`git status` reports `readme.txt` as **modified but not staged**
("Changes not staged for commit"): Git sees that the file differs from the
last commit, but the change will only go into the next commit after a
`git add`.

```bash
git add readme.txt
git commit -m "Add greeting line to readme"
git log --oneline   # -> 2 commits
```

## Part 5 - Exploration

- `git diff`: shows the lines changed in the working directory that are not
  staged yet (`git diff --staged` for what is staged).
- `git log --oneline`: compact history, one line per commit (short hash +
  message).

## Part 6 - Working with branches

| Question | Command |
|---|---|
| List branches | `git branch` (`git branch -a` to include remote ones) |
| Create `feature-script` | `git branch feature-script` |
| Switch to it | `git switch feature-script` (or `git checkout feature-script`) |
| Create + switch to `dev` | `git switch -c dev` (or `git checkout -b dev`) |
| Go back to `feature-script` | `git switch feature-script` |
| Check the current branch | `git branch --show-current` (or `git status`) |

## Part 7 - Create a bash script on a branch

The script is [`install.sh`](install.sh).

```bash
git switch feature-script
touch install.sh            # then write its content
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

`install.sh` **is not there**: it was only committed on `feature-script`.
The working directory reflects the current branch.

```bash
git merge feature-script
ls                     # install.sh shows up
git log --oneline      # the "Add install script" commit is now in main
git branch -d feature-script
```

Since `main` had not moved, Git does a **fast-forward**: it simply moves the
`main` pointer to the `feature-script` commit, without a merge commit.

## Part 9 - Push to GitHub

Create `my-first-repo` on github.com **without a README**, then:

```bash
git remote add origin https://github.com/<user>/my-first-repo.git
git push -u origin main
```

After a refresh, the GitHub page shows the files (`readme.txt`, `install.sh`)
and the commit history.

## Part 10 - Delete and clone

```bash
cd ..
rm -rf my-first-repo
git clone https://github.com/<user>/my-first-repo.git
cd my-first-repo && ls
```

## Part 11 - Full workflow practice

```bash
rm -rf my-first-repo                     # + delete the repo on GitHub (Settings > Delete)
mkdir bash-installer && cd bash-installer
git init
echo "# bash-installer" > README.md
echo "Automatic package installation script." >> README.md
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

1. **Why is version control useful?** Full history, the ability to go back,
   teamwork without overwriting each other's work, remote backup.
2. **Staging vs committing?** *Staging* (`git add`) prepares a selection of
   changes; *committing* permanently records that snapshot in the history.
   Staging makes focused commits possible.
3. **When should you commit?** As soon as a logical unit of work is done and
   works: small and often.
4. **`git init` vs `git clone`?** `init` creates a new empty local repository;
   `clone` copies an existing repository (history included) and sets up the
   `origin` remote.
5. **Why write good commit messages?** To understand later *why* a change was
   made, track down where a bug came from, and make reviews easier.
6. **What are branches for?** Isolating a piece of work (feature, fix)
   without breaking `main`, working in parallel, experimenting.
7. **When to create a branch?** For every new feature, fix or experiment;
   `main` must stay stable and deployable.
