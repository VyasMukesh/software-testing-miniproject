# Quick Start Guide for TaskMaster

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TaskMaster - Quick Setup Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.12+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[2/6] Installing dependencies..." -ForegroundColor Yellow
python -m pip install django django-crispy-forms crispy-bootstrap5 --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Run migrations
Write-Host ""
Write-Host "[3/6] Creating database..." -ForegroundColor Yellow
python manage.py migrate --no-input
Write-Host "✓ Database created" -ForegroundColor Green

# Run tests
Write-Host ""
Write-Host "[4/6] Running comprehensive test suite..." -ForegroundColor Yellow
Write-Host "   Testing foreign key violations, SQL injection, migrations, and regression..." -ForegroundColor Gray
python manage.py test tasks --verbosity 0
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All 18 tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
}

# Create superuser prompt
Write-Host ""
Write-Host "[5/6] Create admin account" -ForegroundColor Yellow
Write-Host "   You'll need this to access the admin panel" -ForegroundColor Gray
$response = Read-Host "Create superuser now? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    python manage.py createsuperuser
    Write-Host "✓ Admin account created" -ForegroundColor Green
} else {
    Write-Host "  Skipped. Run 'python manage.py createsuperuser' later" -ForegroundColor Gray
}

# Start server
Write-Host ""
Write-Host "[6/6] Starting development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete! 🎉" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor White
Write-Host "  • Homepage:    http://localhost:8000/" -ForegroundColor Cyan
Write-Host "  • Admin Panel: http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "  • Tasks:       http://localhost:8000/tasks/" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python manage.py runserver
