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
# Initialize PYTHON_EXEC here with a sensible default
PYTHON_EXEC="python3" # Default to python3

if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    PYTHON_EXEC="python3" # Ensure it matches pip version if possible
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
    # If 'pip' (which is often python2) is found but 'pip3' isn't,
    # it's safer to still default to python3 for the main script unless you
    # specifically know your main.py is python2 compatible, which is unlikely.
    # So, we'll keep it as python3 unless the user's system is very old.
    # If the user only has 'python' (aliased to python2 on old systems),
    # then they might need to manually change this after install.
    # For a robust solution, you might want to try to find `python` / `python3`
    # and map them, but sticking to `python3` is generally safer for modern code.
    if command -v python3 &> /dev/null; then
        PYTHON_EXEC="python3"
    elif command -v python &> /dev/null; then
        PYTHON_EXEC="python" # Fallback to generic 'python' if 'python3' isn't there
    else
        echo "❌ No suitable Python executable found (python3 or python). Please install Python."
        exit 1
    fi

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
# This wrapper ensures 'cd' commands from Mak affect the current shell.
# It captures the output of 'main.py run --shell' and eval's it.

# Path to your Python source script
SCRIPT_SRC_PATH="$CLONE_DIR/src/main.py"

# Determine Python executable (comes from the installer script's detection)
# This will be substituted by the value of PYTHON_EXEC from the install.sh script itself.
PYTHON_EXECUTABLE_TO_USE="$PYTHON_EXEC" # IMPORTANT: Use a new variable name to avoid confusion with the install script's var

# Execute your Python script with the --shell option,
# and eval its output in the current shell.
# All arguments passed to 'mak' are forwarded to main.py's 'run' command.
eval "\$($PYTHON_EXECUTABLE_TO_USE \"\$SCRIPT_SRC_PATH\" run --shell "\$@")"
EOF

sudo chmod +x "$LAUNCHER_PATH"
echo "✅ Launcher script created and made executable."
echo "✅ Mak was installed successfully. Try running 'mak' now. For help, use 'mak --help'"
