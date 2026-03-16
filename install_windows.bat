@echo off
cd /d "%~dp0"
title Zoho Create Invoice Automation — Setup

echo ============================================================
echo   Zoho Create Invoice Automation by leonnel18
echo   Setup Wizard
echo ============================================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found. Launching setup wizard...
echo.
python setup_wizard.py

if errorlevel 1 (
    echo.
    echo [ERROR] The setup wizard encountered an error.
    pause
)
