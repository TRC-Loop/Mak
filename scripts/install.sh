#!/bin/bash

set -euo pipefail

REPO_URL="https://github.com/TRC-Loop/Mak.git"
CLONE_DIR="$HOME/Mak"
SCRIPT_SRC="$CLONE_DIR/src/main.py"
LAUNCHER_PATH="/usr/local/bin/mak"

echo "By installing, you agree to the License."

echo "ℹ️  Cloning repository..."
if [ -d "$CLONE_DIR" ]; then
    echo "⚠️  Directory $CLONE_DIR already exists. Pulling latest changes..."
    git -C "$CLONE_DIR" pull
else
    git clone "$REPO_URL" "$CLONE_DIR"
fi
echo "✅ Repository cloned successfully."

# --- Python Executable and Pip Detection ---
PYTHON_EXEC=""
echo "ℹ️  Checking for Python executable (python3 or python)..."
if command -v python3 &> /dev/null; then
    PYTHON_EXEC="python3"
elif command -v python &> /dev/null; then
    PYTHON_EXEC="python"
else
    echo "❌ Neither 'python3' nor 'python' executable found. Please install Python 3."
    exit 1
fi
echo "✅ Using Python executable: $PYTHON_EXEC"

PIP_CMD=""
echo "ℹ️  Checking for pip or pip3..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ pip or pip3 not found. Please install Python package manager."
    exit 1
fi
echo "✅ Using pip command: $PIP_CMD"

echo "ℹ️  Installing required Python packages with $PIP_CMD..."
"$PIP_CMD" install -r "$CLONE_DIR/requirements.txt"
echo "✅ Packages installed successfully."

# --- Launcher Creation ---
echo "ℹ️  Creating launcher script at $LAUNCHER_PATH..."

# Heredoc ohne Variablexpansion, Variablen werden hart eingetragen
sudo tee "$LAUNCHER_PATH" > /dev/null <<EOF
#!/bin/bash
# Wrapper for running Mak with shell integration

SCRIPT_SRC_PATH="$CLONE_DIR/src/main.py"
PYTHON_EXECUTABLE_TO_USE="$PYTHON_EXEC"

eval "\$("\$PYTHON_EXECUTABLE_TO_USE" "\$SCRIPT_SRC_PATH" run --shell "\$@")"
EOF

sudo chmod +x "$LAUNCHER_PATH"
echo "✅ Launcher script created and made executable."
echo "✅ Mak was installed successfully. Try running 'mak' now. For help, use 'mak --help'"
