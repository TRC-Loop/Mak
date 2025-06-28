Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoUrl = "https://github.com/TRC-Loop/Mak.git"
$cloneDir = "$env:USERPROFILE\Mak"
$scriptSrc = "$cloneDir\src\main.py"
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
$launcherContent = "@echo off`npython `"$scriptSrc`" %*"
Set-Content -Path $launcherPath -Value $launcherContent -Encoding ASCII

Write-Host "✅ Launcher script created."
Write-Host "ℹ️  Please ensure $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps is in your PATH."
