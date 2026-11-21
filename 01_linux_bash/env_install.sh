#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# env_install.sh - sets up a Python development environment
#
# Required features (Part 3 of the exercise):
#   1. pretty_print function (printf + blank lines)
#   2. OS detection through $OSTYPE
#   3. python3 check / installation
#   4. pip check
#   5. Jupyter Notebook installation
#   6. on macOS: `brew doctor`
#
# Implemented bonuses: ANSI colors, timestamped logging, strict mode,
# --dry-run / --verbose / --quiet / --uninstall / --help options.
# ---------------------------------------------------------------------------

# Strict mode: stop on the first error, forbid unset variables,
# make a pipeline fail if any of its commands fails.
set -euo pipefail

# ----------------------------- Configuration -------------------------------
LOG_FILE="${LOG_FILE:-$HOME/env_install.log}"
DRY_RUN=false
VERBOSE=false
QUIET=false
UNINSTALL=false

# ANSI colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
RESET='\033[0m'

# ------------------------------- Functions ----------------------------------

# Write a timestamped line to the log file (audit trail).
log() {
    local level="$1"; shift
    printf '%s [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$level" "$*" >> "$LOG_FILE"
}

# Feature 1: "pretty" output with a blank line before and after.
# Usage: pretty_print "message" [info|success|warning|error]
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

    # In quiet mode, only errors are shown.
    if [[ "$QUIET" == true && "$level" != "error" ]]; then
        return 0
    fi
    printf '\n%b%s%b\n\n' "$color" "$message" "$RESET"
}

# Run a command (or only print it with --dry-run) and log the result.
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
        pretty_print "Command failed: $*" error
        return "$code"
    fi
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [options]

  -n, --dry-run    print the commands without running them
  -v, --verbose    print every command that is run
  -q, --quiet      only print errors
  -u, --uninstall  uninstall Jupyter (undo the script)
  -h, --help       show this help
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
            *) pretty_print "Unknown option: $1" error; usage; exit 1 ;;
        esac
        shift
    done
}

# Feature 2: detect the OS with the OSTYPE environment variable.
detect_os() {
    case "${OSTYPE:-unknown}" in
        darwin*)            OS="macos" ;;
        linux-gnu*|linux*)  OS="linux" ;;
        msys*|cygwin*)      OS="windows" ;;
        *)                  OS="unknown" ;;
    esac
    pretty_print "Detected system: $OS (OSTYPE=${OSTYPE:-?})"
}

# Install a package with the package manager that matches the OS.
install_package() {
    local package="$1"
    case "$OS" in
        macos)
            if ! command_exists brew; then
                pretty_print "Homebrew is required: https://brew.sh" error
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
                pretty_print "No supported package manager found" error
                return 1
            fi
            ;;
        *)
            pretty_print "OS not supported for automatic installation" error
            return 1
            ;;
    esac
}

# Feature 3: is python3 available? If not, install it.
check_python() {
    if command_exists python3; then
        pretty_print "Python already installed: $(python3 --version 2>&1)" success
    else
        pretty_print "python3 not found, installing..." warning
        if [[ "$OS" == "macos" ]]; then
            install_package python
        else
            install_package python3
            install_package python3-pip
        fi
    fi
}

# Feature 4: is pip available?
check_pip() {
    if python3 -m pip --version >/dev/null 2>&1; then
        pretty_print "pip installed: $(python3 -m pip --version)" success
    else
        pretty_print "pip not found, trying ensurepip..." warning
        run python3 -m ensurepip --upgrade
    fi
}

# Feature 5: install Jupyter Notebook (the command depends on the OS).
install_jupyter() {
    if command_exists jupyter; then
        pretty_print "Jupyter already installed: $(jupyter --version 2>/dev/null | head -n 1)" success
        return 0
    fi
    pretty_print "Installing Jupyter Notebook..."
    case "$OS" in
        macos) install_package jupyterlab ;;
        linux) run python3 -m pip install --user notebook ;;
        *)     run python3 -m pip install notebook ;;
    esac
    pretty_print "Jupyter installed ✔ (start it with: jupyter notebook)" success
}

# Feature 6: Homebrew health check on macOS.
brew_health_check() {
    if [[ "$OS" == "macos" ]] && command_exists brew; then
        pretty_print "Running Homebrew diagnostics (brew doctor)..."
        # brew doctor exits non-zero on a mere warning:
        # we don't want strict mode to stop the script because of it.
        if run brew doctor; then
            pretty_print "Homebrew is healthy" success
        else
            pretty_print "brew doctor reported warnings (see above)" warning
        fi
    fi
}

# Bonus: undo the Jupyter installation.
uninstall() {
    pretty_print "Uninstalling Jupyter..." warning
    case "$OS" in
        macos) run brew uninstall jupyterlab || true ;;
        *)     run python3 -m pip uninstall -y notebook || true ;;
    esac
    pretty_print "Uninstall complete" success
}

# --------------------------------- Main -------------------------------------
main() {
    parse_args "$@"
    : > "$LOG_FILE" || true
    pretty_print "=== Development environment setup ==="
    detect_os

    if [[ "$UNINSTALL" == true ]]; then
        uninstall
        exit 0
    fi

    check_python
    check_pip
    install_jupyter
    brew_health_check
    pretty_print "Done! Log: $LOG_FILE" success
}

main "$@"
