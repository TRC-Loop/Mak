
#!/bin/bash
set -euo pipefail

REPO_URL="https://github.com/TRC-Loop/Mak.git"
CLONE_DIR="$HOME/Mak"
SCRIPT_SRC="$CLONE_DIR/src/main.py"
LAUNCHER_PATH="/usr/local/bin/mak"

echo "ℹ️  Cloning repository..."
if [ -d "$CLONE_DIR" ]; then
    echo "⚠️  Directory $CLONE_DIR already exists. Pulling latest changes..."
    git -C "$CLONE_DIR" pull
else
    git clone "$REPO_URL" "$CLONE_DIR"
fi
echo "✅ Repository cloned successfully."

echo "ℹ️  Checking for pip or pip3..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ pip or pip3 not found. Please install Python package manager."
    exit 1
fi

echo "ℹ️  Installing required Python packages with $PIP_CMD..."
$PIP_CMD install -r "$CLONE_DIR/requirements.txt"
echo "✅ Packages installed successfully."

echo "ℹ️  Creating launcher script at $LAUNCHER_PATH..."
sudo tee "$LAUNCHER_PATH" > /dev/null <<EOF
#!/bin/bash
exec python3 "$SCRIPT_SRC" "\$@"
EOF

sudo chmod +x "$LAUNCHER_PATH"
echo "✅ Launcher script created and made executable."
echo "✅ Mak was installed successfully. Try running 'mak' now. For help, use 'mak --help'"
