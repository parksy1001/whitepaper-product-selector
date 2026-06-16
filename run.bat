@echo off
chcp 65001 >nul
title IDIS Product Selector Builder

echo.
echo Current folder: %CD%
echo.
echo Files in current folder:
dir /b
echo.
echo Files in ref folder:
dir /b ref\ 2>nul || echo   ^<ref folder not found^>
echo.
echo Files in Specs folder:
dir /b Specs\ 2>nul || dir /b specs\ 2>nul || echo   ^<Specs folder not found^>
echo.

echo ============================================================
echo   IDIS Product Selector Builder
echo ============================================================
echo.

REM -- Python check --
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://www.python.org
    pause & exit /b 1
)

REM -- openpyxl check --
python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing openpyxl...
    pip install openpyxl --quiet
)

REM -- builder script check --
if not exist "build_idis_selector_v2.py" (
    echo [ERROR] build_idis_selector_v2.py not found.
    pause & exit /b 1
)

if not exist "excel_parser.py" (
    echo [ERROR] excel_parser.py not found.
    pause & exit /b 1
)

REM -- Specs folder check (case-insensitive: Specs or specs) --
set SPECS_DIR=
if exist "Specs\" set SPECS_DIR=Specs
if exist "specs\" set SPECS_DIR=specs
if "%SPECS_DIR%"=="" (
    echo [ERROR] 'Specs' folder not found.
    echo.
    echo   Create a 'Specs' folder and put all SPEC xlsx files in it:
    echo   Specs\
    echo     IPCAM_DOME_기본_SPEC.xlsx
    echo     IPCAM_BULLET_기본_SPEC.xlsx
    echo     IPCAM_BOX_기본_SPEC.xlsx
    echo     NVR_DR2_기본_SPEC.xlsx
    echo     ... etc
    pause & exit /b 1
)
echo   Specs folder: %SPECS_DIR%\

REM -- ref folder check --
if not exist "ref\" (
    echo [ERROR] 'ref' folder not found.
    echo.
    echo   Create a 'ref' folder with:
    echo   ref\
    echo     ipcam_selector_9_1.html
    echo     manual_p79_toolbar.png
    echo     manual_p95_hover.PNG
    echo     manual_p124_timeline.PNG
    echo     manual_p231_stats.PNG
    echo     manual_p259_gdpr.PNG
    echo     manual_p268_acut.PNG
    echo     manual_p269_filter.PNG
    pause & exit /b 1
)

REM ============================================================
REM  STEP 1: Parse Excel SPEC files
REM          -> cameras.json + recorders.json
REM ============================================================
echo [STEP 1/2] Parsing Excel SPEC files from %SPECS_DIR%\...
echo.

python excel_parser.py --specs-dir %SPECS_DIR% --output-dir .
if errorlevel 1 (
    echo [ERROR] Excel parsing failed.
    pause & exit /b 1
)

echo.

REM ============================================================
REM  STEP 2: Build HTML
REM ============================================================
echo [STEP 2/2] Building HTML...
echo.

python build_idis_selector_v2.py
if errorlevel 1 (
    echo [ERROR] HTML build failed.
    pause & exit /b 1
)

REM ============================================================
REM  DONE
REM ============================================================
if exist "IDIS_Product_Selector_Final.html" (
    echo.
    echo ============================================================
    echo   Done!  IDIS_Product_Selector_Final.html
    echo ============================================================
    echo.
    set /p OPEN=   Open in browser? [Y/N] : 
    if /i "%OPEN%"=="Y" (
        start "" "IDIS_Product_Selector_Final.html"
    )
)

echo.
pause
