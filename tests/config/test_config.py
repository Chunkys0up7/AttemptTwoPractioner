"""
Test configuration constants and settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
import logging
from enum import Enum
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Test configuration constants and settings

class TestType(str, Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    SMOKE = "smoke"
    REGRESSION = "regression"
    SLOW = "slow"
    FLAKY = "flaky"
    EXTERNAL = "external"


class TestEnvironment(str, Enum):
    """Test environments."""
    LOCAL = "local"
    CI = "ci"
    STAGING = "staging"
    PRODUCTION = "production"


class TestConfig(BaseModel):
    """Test configuration settings."""
    
    # Environment
    environment: TestEnvironment = TestEnvironment.LOCAL
    testing: bool = True
    
    # Paths
    test_env_dir: Path = Field(default_factory=lambda: Path("tests/test_env"))
    test_data_dir: Path = Field(default_factory=lambda: Path("tests/data"))
    test_reports_dir: Path = Field(default_factory=lambda: Path("tests/reports"))
    
    # API
    api_base_url: str = Field(default_factory=lambda: os.getenv("TEST_API_BASE_URL", "http://localhost:8000"))
    api_timeout: int = Field(default_factory=lambda: int(os.getenv("TEST_API_TIMEOUT", "30")))
    api_max_retries: int = Field(default_factory=lambda: int(os.getenv("TEST_API_MAX_RETRIES", "3")))
    
    # Database
    database_url: str = Field(default_factory=lambda: os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db"))
    database_echo: bool = Field(default_factory=lambda: bool(os.getenv("TEST_DATABASE_ECHO", False)))
    database_pool_size: int = Field(default_factory=lambda: int(os.getenv("TEST_DATABASE_POOL_SIZE", "5")))
    
    # Security
    security_key: str = Field(default_factory=lambda: os.getenv("TEST_SECURITY_KEY", "test-secret-key"))
    security_algorithm: str = Field(default_factory=lambda: os.getenv("TEST_SECURITY_ALGORITHM", "HS256"))
    security_token_expire_minutes: int = Field(default_factory=lambda: int(os.getenv("TEST_SECURITY_TOKEN_EXPIRE_MINUTES", "30")))
    
    # Performance
    performance_max_requests: int = Field(default_factory=lambda: int(os.getenv("PERFORMANCE_MAX_REQUESTS", "1000")))
    performance_window: int = Field(default_factory=lambda: int(os.getenv("PERFORMANCE_WINDOW", "60")))
    performance_target_rps: float = Field(default_factory=lambda: float(os.getenv("PERFORMANCE_TARGET_RPS", "100.0")))
    
    # Rate Limiting
    rate_limit_max_requests: int = Field(default_factory=lambda: int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100")))
    rate_limit_window: int = Field(default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW", "60")))
    
    # Logging
    log_level: str = Field(default_factory=lambda: os.getenv("TEST_LOG_LEVEL", "INFO"))
    log_file: Path = Field(default_factory=lambda: Path("tests/reports/logs/test.log"))
    log_format: str = Field(default_factory=lambda: os.getenv("TEST_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    
    # Coverage
    coverage_dir: Path = Field(default_factory=lambda: Path("tests/reports/coverage"))
    coverage_min: float = Field(default_factory=lambda: float(os.getenv("TEST_COVERAGE_MIN", "80.0")))
    coverage_omit: List[str] = Field(default_factory=lambda: [
        "tests/*",
        "*/__init__.py",
        "mcp/core/config.py",
        "mcp/core/exceptions.py",
        "mcp/core/middleware.py",
        "mcp/core/utils.py"
    ])
    
    # Test Directories
    test_dirs: List[str] = Field(default_factory=lambda: [
        "tests/api",
        "tests/config",
        "tests/data",
        "tests/root",
        "tests/scripts",
        "tests/utils"
    ])
    
    # Test Markers
    test_markers: List[str] = Field(default_factory=lambda: [
        "unit",
        "integration",
        "e2e",
        "performance",
        "security",
        "accessibility",
        "smoke",
        "regression",
        "slow",
        "flaky",
        "external"
    ])
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        
    def __init__(self, **data):
        super().__init__(**data)
        self._setup_environment()
        
    def _setup_environment(self):
        """Set up environment variables."""
        os.environ["TESTING"] = str(self.testing)
        os.environ["DATABASE_URL"] = self.database_url
        os.environ["API_BASE_URL"] = self.api_base_url
        os.environ["SECURITY_KEY"] = self.security_key
        os.environ["SECURITY_ALGORITHM"] = self.security_algorithm
        
        # Create necessary directories
        self.test_env_dir.mkdir(parents=True, exist_ok=True)
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        self.test_reports_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.coverage_dir.mkdir(parents=True, exist_ok=True)
    
    # Database configuration
    DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
    DATABASE_ECHO = bool(os.getenv("TEST_DATABASE_ECHO", False))
    DATABASE_POOL_SIZE = int(os.getenv("TEST_DATABASE_POOL_SIZE", "5"))
    
    # API configuration
    API_BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT = int(os.getenv("TEST_API_TIMEOUT", "30"))
    API_MAX_RETRIES = int(os.getenv("TEST_API_MAX_RETRIES", "3"))
    
    # Security configuration
    SECURITY_KEY = os.getenv("TEST_SECURITY_KEY", "test-secret-key")
    SECURITY_ALGORITHM = os.getenv("TEST_SECURITY_ALGORITHM", "HS256")
    SECURITY_TOKEN_EXPIRE_MINUTES = int(os.getenv("TEST_SECURITY_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Performance configuration
    PERFORMANCE_MAX_REQUESTS = int(os.getenv("PERFORMANCE_MAX_REQUESTS", "1000"))
    PERFORMANCE_WINDOW = int(os.getenv("PERFORMANCE_WINDOW", "60"))
    PERFORMANCE_TARGET_RPS = float(os.getenv("PERFORMANCE_TARGET_RPS", "100.0"))
    
    # Logging configuration
    LOG_LEVEL = os.getenv("TEST_LOG_LEVEL", "INFO")
    LOG_FILE = TEST_REPORTS_DIR / "logs" / "test.log"
    LOG_FORMAT = os.getenv("TEST_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Coverage configuration
    COVERAGE_DIR = TEST_REPORTS_DIR / "coverage"
    COVERAGE_MIN = float(os.getenv("TEST_COVERAGE_MIN", "80.0"))
    COVERAGE_OMIT = [
        "tests/*",
        "*/__init__.py",
        "mcp/core/config.py",
        "mcp/core/exceptions.py",
        "mcp/core/middleware.py",
        "mcp/core/utils.py"
    ]
    
    # Test directories
    TEST_DIRS = [
        "tests/api",
        "tests/config",
        "tests/data",
        "tests/root",
        "tests/scripts",
        "tests/utils"
    ]
    
    # Test markers
    TEST_MARKERS = [
        "unit",
        "integration",
        "e2e",
        "performance",
        "security",
        "accessibility",
        "smoke",
        "regression",
        "slow",
        "flaky",
        "external"
    ]
    
    # Test environment setup
class TestEnvironment:
    """Test environment setup and management."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self._setup_environment()
        self._setup_logging()
        
    def _setup_environment(self):
        """Set up environment variables."""
        os.environ["TESTING"] = str(self.config.testing)
        os.environ["DATABASE_URL"] = self.config.database_url
        os.environ["API_BASE_URL"] = self.config.api_base_url
        os.environ["SECURITY_KEY"] = self.config.security_key
        os.environ["SECURITY_ALGORITHM"] = self.config.security_algorithm
        
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format=self.config.log_format,
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        
    def setup_test_database(self):
        """Set up test database connection."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(
            self.config.database_url,
            echo=self.config.database_echo,
            pool_size=self.config.database_pool_size
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal
        
    def setup_test_api(self):
        """Set up test API client."""
        import httpx
        
        client = httpx.AsyncClient(
            base_url=self.config.api_base_url,
            timeout=self.config.api_timeout,
            max_retries=self.config.api_max_retries
        )
        return client
        
    def setup_test_security(self):
        """Set up test security context."""
        from fastapi.security import OAuth2PasswordBearer
        from jose import jwt
        
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        
        def create_test_token(data: dict, expires_delta: Optional[timedelta] = None):
            """Create test JWT token."""
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.config.security_token_expire_minutes)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.config.security_key, algorithm=self.config.security_algorithm)
            return encoded_jwt
            
        return {
            "oauth2_scheme": oauth2_scheme,
            "create_token": create_test_token
        }
        
    def cleanup(self):
        """Clean up test environment."""
        # Cleanup database
        if hasattr(self, "db_session"):
            self.db_session.close()
        
        # Cleanup API client
        if hasattr(self, "api_client"):
            self.api_client.close()
            
        # Cleanup files
        for dir_path in [self.config.test_data_dir, self.config.test_reports_dir]:
            for file in dir_path.glob("*.tmp"):
                file.unlink()
                
        # Reset environment variables
        for key in ["TESTING", "DATABASE_URL", "API_BASE_URL", "SECURITY_KEY", "SECURITY_ALGORITHM"]:
            os.environ.pop(key, None)

# Export configuration
config = TestConfig()
env = TestEnvironment()
