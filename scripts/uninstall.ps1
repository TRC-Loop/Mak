Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$cloneDir = "$env:USERPROFILE\Mak"
$launcherPath = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\mak.cmd"

Write-Host "ℹ️  Removing launcher script..."
if (Test-Path $launcherPath) {
    Remove-Item $launcherPath -Force
    Write-Host "✅ Launcher script removed."
} else {
    Write-Host "⚠️  Launcher script not found at $launcherPath."
}

Write-Host "ℹ️  Removing cloned repository directory..."
if (Test-Path $cloneDir) {
    Remove-Item $cloneDir -Recurse -Force
    Write-Host "✅ Repository directory removed."
} else {
    Write-Host "⚠️  Repository directory not found at $cloneDir."
}
