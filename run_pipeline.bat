@echo off
cd /d "%~dp0"
echo ============================================================
echo  Zoho Invoice Pipeline — Manual Trigger
echo  %DATE% %TIME%
echo ============================================================
python tools/orchestrator.py
echo.
pause
