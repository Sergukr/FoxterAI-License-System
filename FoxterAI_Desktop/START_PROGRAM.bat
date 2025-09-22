@echo off
color 0A
cls
echo.
echo  =============================================
echo    FoxterAI License Manager v2.0
echo  =============================================
echo.
echo  Starting program...
echo.

cd /d C:\FoxterAI_Desktop

python main.py

if %errorlevel% neq 0 (
    echo.
    echo  =============================================
    echo    ERROR! Python or modules not installed
    echo  =============================================
    echo.
    echo  Installing required modules...
    echo.
    pip install customtkinter requests pandas openpyxl pillow chardet
    echo.
    echo  Trying again...
    echo.
    python main.py
    
    if %errorlevel% neq 0 (
        echo.
        echo  Still not working? Check:
        echo  1. Python is installed
        echo  2. All files are in place
        echo.
    )
)

pause