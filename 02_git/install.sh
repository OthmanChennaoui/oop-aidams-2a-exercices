#!/usr/bin/env bash
# Script de la Part 7 du Git mini exo : met à jour les paquets et installe htop.
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
