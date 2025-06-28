#!/bin/bash
set -euo pipefail

CLONE_DIR="$HOME/Mak"
LAUNCHER_PATH="/usr/local/bin/mak"

echo "ℹ️  Removing launcher script..."
if [ -f "$LAUNCHER_PATH" ]; then
    sudo rm "$LAUNCHER_PATH"
    echo "✅ Launcher script removed."
else
    echo "⚠️  Launcher script not found at $LAUNCHER_PATH."
fi

echo "ℹ️  Removing cloned repository directory..."
if [ -d "$CLONE_DIR" ]; then
    rm -rf "$CLONE_DIR"
    echo "✅ Repository directory removed."
else
    echo "⚠️  Repository directory not found at $CLONE_DIR."
fi
