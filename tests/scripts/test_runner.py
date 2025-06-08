"""
Test runner script that properly sets up the Python environment and runs all tests.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging
from tests.config.test_config import config, env

# Set up logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_tests(
    test_type: str = "all",
    markers: Optional[List[str]] = None,
    files: Optional[List[str]] = None,
    parallel: bool = True,
    coverage: bool = True,
    verbose: bool = False,
    html: bool = False,
    junit: bool = False
) -> int:
    """Run tests with specified options.
    
    Args:
        test_type: Type of tests to run (all, unit, integration, e2e)
        markers: Additional pytest markers to use
        files: Specific test files to run
        parallel: Run tests in parallel
        coverage: Generate coverage report
        verbose: Verbose output
        html: Generate HTML report
        junit: Generate JUnit XML report
    
    Returns:
        Exit code from pytest
    """
    
    try:
        # Set up test environment
        db_session = env.setup_test_database()
        api_client = env.setup_test_api()
        security_context = env.setup_test_security()
        
        # Build pytest command
        pytest_cmd = ["pytest"]
        
        # Add test type specific options
        if test_type == "unit":
            pytest_cmd.extend(["-m", "unit"])
        elif test_type == "integration":
            pytest_cmd.extend(["-m", "integration"])
        elif test_type == "e2e":
            pytest_cmd.extend(["-m", "e2e"])
        
        # Add marker options
        if markers:
            pytest_cmd.extend(["-m", " or ".join(markers)])
            
        # Add file options
        if files:
            pytest_cmd.extend(files)
            
        # Add parallel option
        if parallel:
            pytest_cmd.extend(["-n", "auto"])
            
        # Add coverage options
        if coverage:
            pytest_cmd.extend([
                f"--cov={config.DATABASE_URL}",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=xml"
            ])
            
        # Add report options
        if html:
            pytest_cmd.extend([
                f"--html={config.TEST_REPORTS_DIR}/html/report.html",
                "--self-contained-html"
            ])
            
        if junit:
            pytest_cmd.extend([
                f"--junit-xml={config.TEST_REPORTS_DIR}/junit/results.xml"
            ])
            
        # Add verbosity
        if verbose:
            pytest_cmd.extend(["-v", "-s"])
            
        # Add test directories
        pytest_cmd.extend(config.TEST_DIRS)
            
        logger.info(f"Running tests with command: {' '.join(pytest_cmd)}")
        
        # Run pytest
        result = subprocess.run(
            pytest_cmd,
            capture_output=True,
            text=True,
            env=os.environ
        )
        
        # Print output
        logger.info("\nTest Output:")
        logger.info(result.stdout)
        if result.stderr:
            logger.error("\nTest Errors:")
            logger.error(result.stderr)
            
        # Clean up test environment
        env.cleanup()
        
        return result.returncode
        
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Run project tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "e2e"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--markers",
        nargs="*",
        help="Additional pytest markers to use"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Specific test files to run"
    )
    parser.add_argument(
        "--no-parallel",
        action="store_false",
        dest="parallel",
        help="Disable parallel test execution"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_false",
        dest="coverage",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report"
    )
    parser.add_argument(
        "--junit",
        action="store_true",
        help="Generate JUnit XML report"
    )
    
    args = parser.parse_args()
    
    exit_code = run_tests(
        test_type=args.type,
        markers=args.markers,
        files=args.files,
        parallel=args.parallel,
        coverage=args.coverage,
        verbose=args.verbose,
        html=args.html,
        junit=args.junit
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
