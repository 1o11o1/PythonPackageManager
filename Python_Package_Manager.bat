@echo off
REM Überprüfen, ob Python installiert ist
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Überprüfen, ob pip installiert ist
pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo pip is not installed. Please install pip and try again.
    exit /b 1
)

REM Überprüfen, ob Streamlit installiert ist
pip show streamlit >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing Streamlit...
    pip install streamlit
)

REM Überprüfen, ob andere benötigte Pakete installiert sind
set PACKAGES=streamlit subprocess os signal

for %%P in (%PACKAGES%) do (
    pip show %%P >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo Installing %%P...
        pip install %%P
    )
)

REM Streamlit-App ausführen
streamlit run app.py