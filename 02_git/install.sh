#!/usr/bin/env bash
# Script from Part 7 of the Git mini exo: updates the package lists and installs htop.
set -euo pipefail

echo "Starting installation..."

if [[ "$OSTYPE" == darwin* ]]; then
    brew update
    brew install htop
else
    sudo apt-get update
    sudo apt-get install -y htop
fi

echo "Installation complete!"
