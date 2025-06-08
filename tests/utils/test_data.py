"""
Test data utilities and helpers.
"""
import json
from pathlib import Path
from typing import Dict, Any, List
import random
import string

# Test data directory
TEST_DATA_DIR = Path(__file__).parent.parent / "data"

# Test data files
WORKFLOW_SAMPLES_FILE = TEST_DATA_DIR / "workflow_samples.json"
SECURITY_SAMPLES_FILE = TEST_DATA_DIR / "security_samples.json"

# Load test data
def load_workflow_samples() -> Dict[str, Any]:
    """Load workflow test samples."""
    with open(WORKFLOW_SAMPLES_FILE, 'r') as f:
        return json.load(f)

def load_security_samples() -> Dict[str, Any]:
    """Load security test samples."""
    with open(SECURITY_SAMPLES_FILE, 'r') as f:
        return json.load(f)

def generate_random_workflow(name: str = None) -> Dict[str, Any]:
    """Generate a random workflow."""
    if not name:
        name = f"Test Workflow {random.randint(1, 1000)}"
    
    return {
        "name": name,
        "description": f"Description for {name}",
        "components": [
            {
                "type": "input",
                "name": f"input_{random.randint(1, 100)}",
                "properties": {
                    "label": f"Input {random.randint(1, 100)}",
                    "required": random.choice([True, False])
                }
            }
        ]
    }

def generate_random_headers() -> Dict[str, str]:
    """Generate random headers."""
    return {
        "Content-Type": random.choice(["application/json", "text/plain"]),
        "Accept": random.choice(["application/json", "*/*"]),
        "Host": f"host{random.randint(1, 100)}.com",
        "Origin": f"http://origin{random.randint(1, 100)}.com",
        "Referer": f"http://referer{random.randint(1, 100)}.com",
        "X-CSRF-Token": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        "Authorization": f"Bearer {''.join(random.choices(string.ascii_letters + string.digits, k=32))}"
    }

def generate_random_ip() -> str:
    """Generate a random IP address."""
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))

def generate_random_payload(size: int = 1024) -> str:
    """Generate a random payload of specified size."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

def generate_random_workflow_data(num_components: int = 3) -> Dict[str, Any]:
    """Generate random workflow data with specified number of components."""
    workflow = {
        "name": f"Random Workflow {random.randint(1, 1000)}",
        "description": "Automatically generated workflow",
        "components": [],
        "connections": []
    }
    
    component_types = ["input", "filter", "output"]
    
    for i in range(num_components):
        component_type = random.choice(component_types)
        component = {
            "type": component_type,
            "name": f"{component_type}{i + 1}",
            "properties": {
                "label": f"{component_type} {i + 1}"
            }
        }
        workflow["components"].append(component)
        
        if i > 0:
            workflow["connections"].append({
                "source": f"{component_type}{i}",
                "target": f"{component_type}{i + 1}"
            })
    
    return workflow

def generate_rate_limit_test_data(num_requests: int = 100) -> List[Dict[str, Any]]:
    """Generate test data for rate limiting."""
    return [
        {
            "timestamp": int(time.time() * 1000),
            "ip": generate_random_ip(),
            "path": f"/api/v1/workflows/{random.randint(1, 100)}"
        }
        for _ in range(num_requests)
    ]
