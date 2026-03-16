@echo off
echo Starting ZohoFlow Frontend...

REM Sync source files from Drive to local (excludes node_modules/.next)
robocopy "%~dp0web\frontend" "C:\dev\zohoflow-frontend" /E /XD node_modules .next /NFL /NDL /NJH /NJS /nc /ns /np

REM Install if node_modules not present
if not exist "C:\dev\zohoflow-frontend\node_modules" (
  echo Installing packages...
  cd /d "C:\dev\zohoflow-frontend"
  cmd /c pnpm install --store-dir C:\dev\pnpm-store
)

REM Run from local
cd /d "C:\dev\zohoflow-frontend"
cmd /c pnpm dev
