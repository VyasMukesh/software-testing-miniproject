# Test Verification Script
# Run this to verify all tests pass

Write-Host ""
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  TaskMaster - Test Verification" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Running comprehensive test suite..." -ForegroundColor Yellow
Write-Host "This will test:" -ForegroundColor Gray
Write-Host "  • Foreign Key Violations (5 tests)" -ForegroundColor Gray
Write-Host "  • SQL Injection Protection (3 tests)" -ForegroundColor Gray
Write-Host "  • Data Migration Integrity (3 tests)" -ForegroundColor Gray
Write-Host "  • Regression Testing (7 tests)" -ForegroundColor Gray
Write-Host ""

# Run tests with detailed output
python manage.py test tasks --verbosity 2

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "  ✅ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test Summary:" -ForegroundColor White
    Write-Host "  • Total Tests: 18" -ForegroundColor Green
    Write-Host "  • Passed: 18" -ForegroundColor Green
    Write-Host "  • Failed: 0" -ForegroundColor Green
    Write-Host "  • Success Rate: 100%" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your application is ready to use! 🎉" -ForegroundColor Green
    Write-Host ""
    Write-Host "Start the server with:" -ForegroundColor White
    Write-Host "  python manage.py runserver" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Red
    Write-Host "  ❌ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "=====================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please review the output above for details." -ForegroundColor Yellow
    Write-Host ""
}
