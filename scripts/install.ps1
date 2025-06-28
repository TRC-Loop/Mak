Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "By installing, you agree to the License."

$repoUrl = "https://github.com/TRC-Loop/Mak.git"
$cloneDir = "$env:USERPROFILE\Mak"
$scriptSrc = "$cloneDir\src\main.py"
# The launcher will be a .cmd file to be directly callable in cmd/PowerShell
$launcherPath = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\mak.cmd"

Write-Host "ℹ️  Cloning repository..."
if (Test-Path $cloneDir) {
    Write-Host "⚠️  Directory $cloneDir already exists. Pulling latest changes..."
    git -C $cloneDir pull
} else {
    git clone $repoUrl $cloneDir
}
Write-Host "✅ Repository cloned successfully."

Write-Host "ℹ️  Checking for pip or pip3..."
$pipCmd = $null
if (Get-Command pip3 -ErrorAction SilentlyContinue) {
    $pipCmd = "pip3"
} elseif (Get-Command pip -ErrorAction SilentlyContinue) {
    $pipCmd = "pip"
} else {
    Write-Error "❌ pip or pip3 not found. Please install Python package manager."
    exit 1
}

Write-Host "ℹ️  Installing required Python packages with $pipCmd..."
& $pipCmd install -r "$cloneDir\requirements.txt"
Write-Host "✅ Packages installed successfully."

Write-Host "ℹ️  Creating launcher script at $launcherPath..."
# --- START OF MODIFIED LAUNCHER CONTENT ---
# This batch script will execute the Python script with --shell,
# capture its output, and then execute each line of output
# in the current batch session, which includes 'cd' commands.
$launcherContent = @"
@echo off
REM This wrapper ensures 'cd' commands from Mak affect the current shell.
REM It captures the output of 'main.py run --shell' and executes it.

REM Get the script's source directory (adjust if main.py moves)
SET "SCRIPT_SRC_PATH=%USERPROFILE%\Mak\src\main.py"

REM Determine Python executable (use 'py' launcher for robustness on Windows)
SET "PYTHON_EXEC=py"

REM Execute your Python script with the --shell option,
REM and then execute the output for the current batch session.
REM /v:on enables delayed expansion for '%%i' inside the loop,
REM though not strictly needed for just '%%i'.
FOR /F "usebackq tokens=*" %%i IN (`%PYTHON_EXEC% "%SCRIPT_SRC_PATH%" run --shell %*`) DO (
    call %%i
)
"@
# --- END OF MODIFIED LAUNCHER CONTENT ---
Set-Content -Path $launcherPath -Value $launcherContent -Encoding ASCII

Write-Host "✅ Launcher script created."
Write-Host "ℹ️  Please ensure $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps is in your PATH. This is usually managed by Windows."
Write-Host "✅ Mak was installed successfully. Try running 'mak' now. For help, use 'mak --help'"
