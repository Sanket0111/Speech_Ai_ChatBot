@echo off
echo Speech AI System Runner

:: Set Python path to include current directory
set PYTHONPATH=%CD%

:: Check if virtual environment exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo Installing dependencies...
    pip install -r requirements.txt
)

:: Run Streamlit app
echo Starting Speech AI application...
streamlit run app/app.py
pause 