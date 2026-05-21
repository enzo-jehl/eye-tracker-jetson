# PowerShell equivalent of `make check`.
# Runs ruff + black --check + mypy + pytest. Stops at the first failure.
#
# Usage (from repo root, with the venv activated):
#   .\scripts\check.ps1

$ErrorActionPreference = "Stop"

Write-Host "==> ruff" -ForegroundColor Cyan
ruff check src tests scripts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> black --check" -ForegroundColor Cyan
black --check src tests scripts
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> mypy" -ForegroundColor Cyan
mypy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> pytest" -ForegroundColor Cyan
pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "`nAll checks passed." -ForegroundColor Green
