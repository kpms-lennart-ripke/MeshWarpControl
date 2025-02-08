$VenvPath = ".\.venv"

# Create virtual environment if it doesn't exist
if (-Not (Test-Path -Path $VenvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvPath
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& "$VenvPath\Scripts\Activate.ps1"

# Upgrade pip and install dependencies
Write-Host "Upgrading pip..."
python.exe -m pip install --upgrade pip

Write-Host "Installing dependencies..."
python.exe -m pip install -r "requirements.txt"