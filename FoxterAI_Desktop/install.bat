@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   FoxterAI License Manager
echo   Installation of dependencies
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher:
    echo https://www.python.org/downloads/
    echo.
    echo When installing, make sure to check:
    echo [x] Add Python to PATH
    echo.
    pause
    exit /b
)

echo Python detected:
python --version
echo.

REM Update pip
echo Updating pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing required packages...
echo --------------------------------
pip install customtkinter==5.2.0
pip install requests==2.31.0
pip install pandas==2.0.3
pip install openpyxl==3.1.2
pip install pillow==10.0.0
pip install chardet

echo.
echo ========================================
echo   Installation completed!
echo ========================================
echo.
echo Now you can run the program:
echo   python main.py
echo.
echo Or create an EXE file:
echo   build.bat
echo.
pause