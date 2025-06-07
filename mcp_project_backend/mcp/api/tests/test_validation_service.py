from mcp.api.services.code_validation_service import (
    validate_syntax,
    validate_types,
    scan_security,
    analyze_performance,
    ValidationServiceError
)
import pytest

def test_validate_syntax_valid():
    code = "print('hello')"
    assert validate_syntax(code) is True

def test_validate_syntax_invalid():
    code = "print('hello'"
    with pytest.raises(ValidationServiceError):
        validate_syntax(code)

def test_validate_types_valid():
    code = "x: int = 5"
    assert validate_types(code) is True

def test_validate_types_invalid():
    code = "x: int = 'string'"
    with pytest.raises(ValidationServiceError):
        validate_types(code)

def test_scan_security_safe():
    code = "print('safe')"
    assert scan_security(code) is True

def test_scan_security_unsafe():
    code = "import os; os.system('rm -rf /')"
    with pytest.raises(ValidationServiceError):
        scan_security(code)

def test_analyze_performance_good():
    code = "for i in range(10): pass"
    assert analyze_performance(code) == "Good"

def test_analyze_performance_bad():
    code = "for i in range(10000000): pass"
    result = analyze_performance(code)
    assert result in ["Bad", "Needs Improvement"] 