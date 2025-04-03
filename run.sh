#!/bin/bash
# Speech AI System Runner Script

# Set Python path to include current directory
export PYTHONPATH=$PWD

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run Streamlit app
echo "Starting Speech AI application..."
streamlit run app/app.py 