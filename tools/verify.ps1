param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/2] Compile" -ForegroundColor Cyan
& $Python -m compileall visulite tests

Write-Host "[2/2] Unit tests" -ForegroundColor Cyan
& $Python -m unittest discover -s tests -p "test_*.py"

