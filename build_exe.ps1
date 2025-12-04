# Build script untuk membuat .exe dari audiogram_plotter.py
# Jalankan: .\build_exe.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Audiogram Plotter - Build to EXE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller installed
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
$pyinstaller = pip list | Select-String "pyinstaller"
if (-not $pyinstaller) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install PyInstaller!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "PyInstaller found: $pyinstaller" -ForegroundColor Green
}

Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host ""

# Clean previous build
if (Test-Path ".\dist") {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".\dist"
}
if (Test-Path ".\build") {
    Remove-Item -Recurse -Force ".\build"
}
if (Test-Path ".\audiogram_plotter.spec") {
    Remove-Item -Force ".\audiogram_plotter.spec"
}

# Build command
$buildCmd = @"
pyinstaller --noconsole --onefile --name "AudiogramPlotter" --add-data "calib.json;." --icon=NONE audiogram_plotter.py
"@

Write-Host "Running: $buildCmd" -ForegroundColor Cyan
Invoke-Expression $buildCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location:" -ForegroundColor Cyan
    Write-Host "  .\dist\AudiogramPlotter.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "To test, run:" -ForegroundColor Yellow
    Write-Host "  .\dist\AudiogramPlotter.exe" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Build FAILED!" -ForegroundColor Red
    Write-Host "Check errors above." -ForegroundColor Red
    exit 1
}
