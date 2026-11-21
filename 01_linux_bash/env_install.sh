#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# env_install.sh - configure un environnement de développement Python
#
# Fonctionnalités demandées (Part 3 de l'exo) :
#   1. fonction pretty_print (printf + lignes vides)
#   2. détection de l'OS via $OSTYPE
#   3. vérification / installation de python3
#   4. vérification de pip
#   5. installation de Jupyter Notebook
#   6. sur macOS : `brew doctor`
#
# Bonus implémentés : couleurs ANSI, logging horodaté, strict mode,
# options --dry-run / --verbose / --quiet / --uninstall / --help.
# ---------------------------------------------------------------------------

# Strict mode : stop à la première erreur, variables non définies interdites,
# un pipeline échoue si une de ses commandes échoue.
set -euo pipefail

# ----------------------------- Configuration -------------------------------
LOG_FILE="${LOG_FILE:-$HOME/env_install.log}"
DRY_RUN=false
VERBOSE=false
QUIET=false
UNINSTALL=false

# Couleurs ANSI
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

# ------------------------------- Fonctions ----------------------------------

# Écrit une ligne horodatée dans le fichier de log (audit trail).
log() {
    local level="$1"; shift
    printf '%s [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$level" "$*" >> "$LOG_FILE"
}

# Feature 1 : affichage "joli" avec une ligne vide avant et après.
# Usage : pretty_print "message" [info|success|warning|error]
pretty_print() {
    local message="$1"
    local level="${2:-info}"
    local color="$BLUE"

    case "$level" in
        success) color="$GREEN" ;;
        warning) color="$YELLOW" ;;
        error)   color="$RED" ;;
    esac

    log "$(printf '%s' "$level" | tr '[:lower:]' '[:upper:]')" "$message"

    # En mode quiet on n'affiche que les erreurs.
    if [[ "$QUIET" == true && "$level" != "error" ]]; then
        return 0
    fi
    printf '\n%b%s%b\n\n' "$color" "$message" "$RESET"
}

# Exécute une commande (ou l'affiche seulement en --dry-run) et logge le résultat.
run() {
    log "CMD" "$*"
    if [[ "$DRY_RUN" == true ]]; then
        printf '%b[dry-run]%b %s\n' "$YELLOW" "$RESET" "$*"
        return 0
    fi
    if [[ "$VERBOSE" == true ]]; then
        printf '%b+ %s%b\n' "$BLUE" "$*" "$RESET"
    fi
    if "$@"; then
        log "OK" "$*"
    else
        local code=$?
        log "FAIL" "$* (exit $code)"
        pretty_print "La commande a échoué : $*" error
        return "$code"
    fi
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

usage() {
    cat <<EOF
Usage : $(basename "$0") [options]

  -n, --dry-run    affiche les commandes sans les exécuter
  -v, --verbose    affiche chaque commande exécutée
  -q, --quiet      n'affiche que les erreurs
  -u, --uninstall  désinstalle Jupyter (annule le script)
  -h, --help       affiche cette aide
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -n|--dry-run)   DRY_RUN=true ;;
            -v|--verbose)   VERBOSE=true ;;
            -q|--quiet)     QUIET=true ;;
            -u|--uninstall) UNINSTALL=true ;;
            -h|--help)      usage; exit 0 ;;
            *) pretty_print "Option inconnue : $1" error; usage; exit 1 ;;
        esac
        shift
    done
}

# Feature 2 : détection de l'OS grâce à la variable d'environnement OSTYPE.
detect_os() {
    case "${OSTYPE:-unknown}" in
        darwin*)            OS="macos" ;;
        linux-gnu*|linux*)  OS="linux" ;;
        msys*|cygwin*)      OS="windows" ;;
        *)                  OS="unknown" ;;
    esac
    pretty_print "Système détecté : $OS (OSTYPE=${OSTYPE:-?})"
}

# Installe un paquet avec le gestionnaire de paquets adapté à l'OS.
install_package() {
    local package="$1"
    case "$OS" in
        macos)
            if ! command_exists brew; then
                pretty_print "Homebrew est requis : https://brew.sh" error
                return 1
            fi
            run brew install "$package"
            ;;
        linux)
            if command_exists apt-get; then
                run sudo apt-get update
                run sudo apt-get install -y "$package"
            elif command_exists dnf; then
                run sudo dnf install -y "$package"
            elif command_exists yum; then
                run sudo yum install -y "$package"
            else
                pretty_print "Aucun gestionnaire de paquets supporté trouvé" error
                return 1
            fi
            ;;
        *)
            pretty_print "OS non supporté pour l'installation automatique" error
            return 1
            ;;
    esac
}

# Feature 3 : python3 présent ? sinon on l'installe.
check_python() {
    if command_exists python3; then
        pretty_print "Python déjà installé : $(python3 --version 2>&1)" success
    else
        pretty_print "python3 introuvable, installation..." warning
        if [[ "$OS" == "macos" ]]; then
            install_package python
        else
            install_package python3
            install_package python3-pip
        fi
    fi
}

# Feature 4 : pip disponible ?
check_pip() {
    if python3 -m pip --version >/dev/null 2>&1; then
        pretty_print "pip installé : $(python3 -m pip --version)" success
    else
        pretty_print "pip introuvable, tentative avec ensurepip..." warning
        run python3 -m ensurepip --upgrade
    fi
}

# Feature 5 : installation de Jupyter Notebook (commande différente selon l'OS).
install_jupyter() {
    if command_exists jupyter; then
        pretty_print "Jupyter déjà présent : $(jupyter --version 2>/dev/null | head -n 1)" success
        return 0
    fi
    pretty_print "Installation de Jupyter Notebook..."
    case "$OS" in
        macos) install_package jupyterlab ;;
        linux) run python3 -m pip install --user notebook ;;
        *)     run python3 -m pip install notebook ;;
    esac
    pretty_print "Jupyter installé ✔ (lancer avec : jupyter notebook)" success
}

# Feature 6 : diagnostic Homebrew sur macOS.
brew_health_check() {
    if [[ "$OS" == "macos" ]] && command_exists brew; then
        pretty_print "Diagnostic Homebrew (brew doctor)..."
        # brew doctor renvoie un code != 0 dès qu'il y a un simple warning :
        # on ne veut pas que le strict mode arrête le script pour ça.
        if run brew doctor; then
            pretty_print "Homebrew est en bonne santé" success
        else
            pretty_print "brew doctor a signalé des avertissements (voir ci-dessus)" warning
        fi
    fi
}

# Bonus : annule l'installation de Jupyter.
uninstall() {
    pretty_print "Désinstallation de Jupyter..." warning
    case "$OS" in
        macos) run brew uninstall jupyterlab || true ;;
        *)     run python3 -m pip uninstall -y notebook || true ;;
    esac
    pretty_print "Désinstallation terminée" success
}

# --------------------------------- Main -------------------------------------
main() {
    parse_args "$@"
    : > "$LOG_FILE" || true
    pretty_print "=== Configuration de l'environnement de développement ==="
    detect_os

    if [[ "$UNINSTALL" == true ]]; then
        uninstall
        exit 0
    fi

    check_python
    check_pip
    install_jupyter
    brew_health_check
    pretty_print "Terminé ! Log : $LOG_FILE" success
}

main "$@"
