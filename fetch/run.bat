@echo off
TITLE CryptoBot V2 Launcher

REM === ROOT PATH (relative to where this bat is located) ===
SET BASE_PATH=%~dp0
SET VENV_FOLDER="%BASE_PATH%venv\Scripts\activate.bat"
SET SCRIPT_PATH="%BASE_PATH%crypto-trading\cryptotradingv2"

echo ===========================================
echo ==    MEMULAI CRYPTOBOT V2 LAUNCHER      ==
echo ===========================================

REM Check venv
if not exist %VENV_FOLDER% (
    echo [ERROR] Virtual environment not found at: %VENV_FOLDER%
    pause
    exit /b
)

REM Install requirements
echo [INFO] Installing/updating dependencies...
call "%BASE_PATH%venv\Scripts\python.exe" -m pip install -r %SCRIPT_PATH%\requirements.txt
echo [SUCCESS] Requirements installed.
echo.

REM === Build Windows Terminal command ===
wt.exe ^
    new-tab --title "Technical Agent" cmd /k "call %VENV_FOLDER% && cd /d %SCRIPT_PATH% && python technical_agent.py" ^
    ; new-tab --title "News Agent" cmd /k "call %VENV_FOLDER% && cd /d %SCRIPT_PATH% && python news_agent.py" ^
    ; new-tab --title "Whale Agent" cmd /k "call %VENV_FOLDER% && cd /d %SCRIPT_PATH% && python whale_agent.py" ^
    ; new-tab --title "Risk Manager" cmd /k "call %VENV_FOLDER% && cd /d %SCRIPT_PATH% && python enhanced_risk_manager_agent.py" ^
    ; new-tab --title "Signal Orchestrator" cmd /k "call %VENV_FOLDER% && cd /d %SCRIPT_PATH% && python fixed_comprehensive_signal_agent.py" ^
    ; new-tab --title "User Interface" cmd /k "call %VENV_FOLDER% && cd /d %SCRIPT_PATH% && python comprehensive_user_agent.py"

echo.
echo =================================================================
echo == [DONE] All agents are running in Windows Terminal tabs.     ==
echo =================================================================
echo.
pause
