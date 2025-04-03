# Speech AI System Runner Script

# Set Python path to include current directory
$env:PYTHONPATH = $PWD.Path

# Check if virtual environment exists
if (Test-Path -Path "venv") {
    Write-Host "Activating virtual environment..."
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
}

# Run Streamlit app
Write-Host "Starting Speech AI application..."
streamlit run app/app.py 