"""
Test environment setup script.
"""
import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import List
from tests.config.env_config import TEST_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment() -> None:
    """Set up the test environment."""
    logger.info("Setting up test environment...")
    
    # Create virtual environment
    create_virtual_env()
    
    # Install dependencies
    install_dependencies()
    
    # Verify environment
    verify_environment()

def create_virtual_env() -> None:
    """Create virtual environment."""
    logger.info("Creating virtual environment...")
    env_dir = Path(os.getenv('TEST_ENV', 'test_env'))
    
    if env_dir.exists():
        logger.info("Removing existing virtual environment...")
        subprocess.run(["rm", "-rf", str(env_dir)])
    
    subprocess.run(["python", "-m", "venv", str(env_dir)])
    logger.info("Virtual environment created")

def install_dependencies() -> None:
    """Install test dependencies."""
    logger.info("Installing dependencies...")
    env_dir = Path(os.getenv('TEST_ENV', 'test_env'))
    
    # Install test dependencies
    subprocess.run([
        str(env_dir / "Scripts" / "pip"),
        "install",
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "pytest-xdist"
    ])
    
    # Install project requirements
    subprocess.run([
        str(env_dir / "Scripts" / "pip"),
        "install",
        "-r",
        "requirements.txt"
    ])
    
    # Install project in development mode
    subprocess.run([
        str(env_dir / "Scripts" / "pip"),
        "install",
        "-e",
        "."
    ])

def verify_environment() -> None:
    """Verify test environment."""
    logger.info("Verifying test environment...")
    env_dir = Path(os.getenv('TEST_ENV', 'test_env'))
    
    # Verify Python version
    result = subprocess.run([
        str(env_dir / "Scripts" / "python"),
        "--version"
    ], capture_output=True)
    logger.info(f"Python version: {result.stdout.decode().strip()}")
    
    # Verify pytest installation
    result = subprocess.run([
        str(env_dir / "Scripts" / "pytest"),
        "--version"
    ], capture_output=True)
    logger.info(f"pytest version: {result.stdout.decode().strip()}")

if __name__ == "__main__":
    setup_environment()
