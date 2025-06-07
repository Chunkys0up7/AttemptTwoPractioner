# Set PYTHONPATH to include the project root
$env:PYTHONPATH = "C:\projects\AttemptTwoPractioner\mcp_project_backend"

# Run pytest with the full path to the test file
python -m pytest C:\projects\AttemptTwoPractioner\tests\api\middleware\test_security_middleware.py -v -s
