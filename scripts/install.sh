#!/bin/bash

set -euo pipefail

REPO_URL="https://github.com/TRC-Loop/Mak.git"
CLONE_DIR="$HOME/Mak"
SCRIPT_SRC="$CLONE_DIR/src/main.py"
LAUNCHER_PATH="/usr/local/bin/mak" # Standard location for user-installed binaries

echo "By installing, you agree to the License."

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
# --- START OF MODIFIED LAUNCHER CONTENT ---
# This shell script will execute the Python script with --shell,
# capture its output using command substitution, and then eval it
# in the current shell context.
sudo tee "$LAUNCHER_PATH" > /dev/null <<EOF
#!/bin/bash
# This wrapper ensures 'cd' commands from Mak affect the current shell.
# It captures the output of 'main.py run --shell' and eval's it.

# Path to your Python source script
SCRIPT_SRC_PATH="$CLONE_DIR/src/main.py"

# Determine Python executable (use 'python3' for modern systems, 'python' might be older 2.x)
PYTHON_EXEC="python3"

# Execute your Python script with the --shell option,
# and eval its output in the current shell.
# All arguments passed to 'mak' are forwarded to main.py's 'run' command.
eval "\$($PYTHON_EXEC \"\$SCRIPT_SRC_PATH\" run --shell "\$@")"
EOF
# --- END OF MODIFIED LAUNCHER CONTENT ---

sudo chmod +x "$LAUNCHER_PATH"
echo "✅ Launcher script created and made executable."
echo "✅ Mak was installed successfully. Try running 'mak' now. For help, use 'mak --help'"
