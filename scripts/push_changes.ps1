# PowerShell helper — from repo root:
#   .\scripts\push_changes.ps1 "Your commit message"

param(
    [Parameter(Mandatory = $true)]
    [string]$Message
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

git add .
git commit -m $Message
if ($LASTEXITCODE -ne 0) {
    Write-Error "Commit failed."
    exit 1
}
git push
if ($LASTEXITCODE -ne 0) {
    Write-Error "Push failed."
    exit 1
}
Write-Host "Pushed successfully."
