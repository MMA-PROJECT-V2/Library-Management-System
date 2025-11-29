# Create Books Service Configuration Files
# Run from: backend/books_service directory

Write-Host "Creating Books Service Configuration Files..." -ForegroundColor Cyan
Write-Host ""

$currentDir = Get-Location
Write-Host "Current directory: $currentDir" -ForegroundColor Yellow

# Verify we're in books_service directory
if (-not (Test-Path "manage.py")) {
    Write-Host "ERROR: manage.py not found!" -ForegroundColor Red
    Write-Host "Make sure you're in the backend/books_service directory" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "tests")) {
    Write-Host "ERROR: tests directory not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Directory verified" -ForegroundColor Green
Write-Host ""

# Create conftest.py
Write-Host "Creating conftest.py..." -ForegroundColor Yellow

$conftestContent = @'
import os
import sys
import django

# Ensure Django settings are configured for tests within books_service
PROJECT_ROOT = os.path.dirname(__file__)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'books_service.settings')

# Configure Django for pytest
django.setup()
'@

Set-Content -Path "conftest.py" -Value $conftestContent -Encoding UTF8
Write-Host "✓ Created: conftest.py" -ForegroundColor Green

# Create pytest.ini
Write-Host "Creating pytest.ini..." -ForegroundColor Yellow

$pytestIniContent = @'
[pytest]
# pytest configuration for books_service microservice
# This allows running tests from within the backend/books_service directory
DJANGO_SETTINGS_MODULE = books_service.settings
python_files = test_*.py *_tests.py
testpaths = tests
addopts = -q --junitxml=pytest_results.xml --cov=books --cov=books_service --cov-report=term --cov-report=xml:coverage.xml
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
'@

Set-Content -Path "pytest.ini" -Value $pytestIniContent -Encoding UTF8
Write-Host "✓ Created: pytest.ini" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify files
Write-Host "Verifying files..." -ForegroundColor Yellow
$files = @("conftest.py", "pytest.ini", "manage.py", "tests")

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file NOT found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Structure:" -ForegroundColor Cyan
Write-Host "  backend/books_service/" -ForegroundColor White
Write-Host "  ├── conftest.py       ✓" -ForegroundColor Gray
Write-Host "  ├── pytest.ini        ✓" -ForegroundColor Gray
Write-Host "  ├── manage.py         ✓" -ForegroundColor Gray
Write-Host "  ├── requirements.txt  ✓" -ForegroundColor Gray
Write-Host "  ├── books_service/    ✓" -ForegroundColor Gray
Write-Host "  ├── books/            ✓" -ForegroundColor Gray
Write-Host "  └── tests/            ✓" -ForegroundColor Gray
Write-Host "      ├── __init__.py" -ForegroundColor Gray
Write-Host "      └── test_*.py (8 files)" -ForegroundColor Gray

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. pytest" -ForegroundColor White
Write-Host ""
Write-Host "✨ Ready to run tests!" -ForegroundColor Green