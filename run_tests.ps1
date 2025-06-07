#!/bin/powershell

# Configuration
$PROJECT_ROOT = (Get-Item $PSScriptRoot).Parent.FullName
$BACKEND_DIR = Join-Path $PROJECT_ROOT "mcp_project_backend"
$TEST_ENV = Join-Path $PROJECT_ROOT "test_env"
$TEST_SCRIPT = Join-Path $PROJECT_ROOT "test_runner.py"

# Function to log messages
function Write-Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [string]$Level = "INFO"
    )
    Write-Host "[$Level] $Message" -ForegroundColor Cyan
}

# Function to create virtual environment
function Create-VirtualEnv {
    Write-Log "Creating virtual environment..."
    python -m venv $TEST_ENV
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to create virtual environment" -Level "ERROR"
        exit 1
    }
}

# Function to install dependencies
function Install-Dependencies {
    Write-Log "Installing dependencies..."
    
    # Activate virtual environment
    $activateScript = Join-Path $TEST_ENV "Scripts\activate.ps1"
    if (Test-Path $activateScript) {
        . $activateScript
    }
    
    # Install test dependencies first
    Write-Log "Installing test dependencies..."
    pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to install test dependencies" -Level "ERROR"
        exit 1
    }
    
    # Install project requirements
    Write-Log "Installing project requirements..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to install requirements" -Level "ERROR"
        exit 1
    }
    
    # Install project in development mode
    Write-Log "Installing project in development mode..."
    pip install -e .
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to install project in development mode" -Level "ERROR"
        exit 1
    }
    
    # Verify installations
    Write-Log "Verifying installations..."
    python -m pytest --version
    if ($LASTEXITCODE -ne 0) {
        Write-Log "pytest installation verification failed" -Level "ERROR"
        exit 1
    }
    
    Write-Log "All dependencies installed successfully"
}

# Function to run tests
function Run-Tests {
    Write-Log "Running test runner script..."
    python $TEST_SCRIPT
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Test execution failed" -Level "ERROR"
        exit 1
    }
    Write-Log "All tests passed!" -Level "SUCCESS"
}

# Main execution
try {
    # Clean up existing virtual environment
    if (Test-Path $TEST_ENV) {
        Remove-Item -Recurse -Force $TEST_ENV
    }
    
    # Create and set up environment
    Create-VirtualEnv
    Install-Dependencies
    
    # Run tests
    Run-Tests
} catch {
    Write-Log "An error occurred: $_" -Level "ERROR"
    exit 1
}
