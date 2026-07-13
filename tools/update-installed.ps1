param(
  [string]$RepoPath = "C:\Users\AIRI\Documents\Q&A_Bot\work\reuse-scout-publish",
  [string]$InstallPath = "C:\Users\AIRI\.codex\skills\reuse-scout",
  [string]$Validator = "C:\Users\AIRI\.codex\skills\.system\skill-creator\scripts\quick_validate.py"
)

$ErrorActionPreference = "Stop"

function Require-Path {
  param([string]$Path, [string]$Label)
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "$Label not found: $Path"
  }
}

function Get-FullPath {
  param([string]$Path)
  return [System.IO.Path]::GetFullPath($Path)
}

Require-Path $RepoPath "Repo path"
Require-Path $Validator "Validator"

$repoFull = Get-FullPath $RepoPath
$installFull = Get-FullPath $InstallPath
$expectedInstall = Get-FullPath "C:\Users\AIRI\.codex\skills\reuse-scout"

if ($installFull -ne $expectedInstall) {
  throw "Refusing to update unexpected install path: $installFull"
}

Write-Host "Pulling latest reuse-scout from GitHub..."
Set-Location -LiteralPath $repoFull
git pull --ff-only

Write-Host "Syncing skill files to $installFull..."
New-Item -ItemType Directory -Force -Path $installFull | Out-Null

$items = @(
  "SKILL.md",
  "agents",
  "references",
  "scripts"
)

foreach ($item in $items) {
  $src = Join-Path $repoFull $item
  $dst = Join-Path $installFull $item
  $dstFull = Get-FullPath $dst

  Require-Path $src "Required skill item"

  if (-not $dstFull.StartsWith($installFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to remove path outside install directory: $dstFull"
  }

  if (Test-Path -LiteralPath $dstFull) {
    Remove-Item -LiteralPath $dstFull -Recurse -Force
  }

  Copy-Item -LiteralPath $src -Destination $dstFull -Recurse -Force
}

Write-Host "Validating installed skill..."
$env:PYTHONUTF8 = "1"
python $Validator $installFull

Write-Host "reuse-scout installed skill updated successfully."
