param(
  # Optional: pass an explicit python path, e.g.
  #   .\tools\build_exe.ps1 -Python "D:/tools/miniconda3/envs/visulite/python.exe"
  [string]$Python = $env:VISULITE_PYTHON
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $repoRoot
try {
  if (-not $Python) {
    $Python = "python"
  }

  # Print the interpreter being used (helps avoid packaging with the wrong env).
  & $Python -c "import sys; print(sys.executable)"

  & $Python -m PyInstaller --noconfirm --clean .\VisuLite.spec

  Write-Host ("Built: {0}" -f (Join-Path $repoRoot "dist\VisuLite\VisuLite.exe"))
} finally {
  Pop-Location
}

