"""
Performance test suite for workflow functionality.
"""
import pytest
import time
from typing import Dict, List
import random
import string
from fastapi.testclient import TestClient

@pytest.mark.performance
def test_workflow_creation_performance(test_client: TestClient, sample_workflow_data: Dict[str, Any]):
    """Test performance of workflow creation."""
    num_workflows = 100
    total_time = 0
    
    for i in range(num_workflows):
        # Generate unique workflow name
        workflow_name = f"Performance Test {i}"
        workflow_data = {**sample_workflow_data, "name": workflow_name}
        
        start_time = time.time()
        response = test_client.post("/api/workflows", json=workflow_data)
        end_time = time.time()
        
        assert response.status_code == 201
        total_time += (end_time - start_time)
    
    avg_time = total_time / num_workflows
    assert avg_time < 0.1  # Should take less than 100ms per workflow

@pytest.mark.performance
def test_workflow_execution_performance(test_client: TestClient):
    """Test performance of workflow execution."""
    # Create a workflow with multiple components
    workflow_data = {
        "name": "Performance Test Workflow",
        "description": "Workflow for performance testing",
        "components": [
            {"type": "input", "name": "input1"},
            {"type": "filter", "name": "filter1"},
            {"type": "output", "name": "output1"}
        ],
        "connections": [
            {"source": "input1", "target": "filter1"},
            {"source": "filter1", "target": "output1"}
        ]
    }
    
    # Create workflow
    create_response = test_client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    workflow_id = create_response.json()["id"]
    
    # Execute workflow multiple times
    num_executions = 100
    total_time = 0
    
    for _ in range(num_executions):
        start_time = time.time()
        execute_response = test_client.post(f"/api/workflows/{workflow_id}/execute")
        end_time = time.time()
        
        assert execute_response.status_code == 200
        total_time += (end_time - start_time)
    
    avg_time = total_time / num_executions
    assert avg_time < 0.2  # Should take less than 200ms per execution

@pytest.mark.performance
def test_concurrent_workflow_execution(test_client: TestClient):
    """Test concurrent workflow execution performance."""
    import threading
    from queue import Queue
    
    # Create a workflow
    workflow_data = {
        "name": "Concurrent Test Workflow",
        "description": "Workflow for concurrent testing",
        "components": [
            {"type": "input", "name": "input1"},
            {"type": "filter", "name": "filter1"},
            {"type": "output", "name": "output1"}
        ],
        "connections": [
            {"source": "input1", "target": "filter1"},
            {"source": "filter1", "target": "output1"}
        ]
    }
    
    create_response = test_client.post("/api/workflows", json=workflow_data)
    assert create_response.status_code == 201
    workflow_id = create_response.json()["id"]
    
    # Create thread pool
    num_threads = 10
    results = Queue()
    
    def execute_workflow():
        start_time = time.time()
        response = test_client.post(f"/api/workflows/{workflow_id}/execute")
        end_time = time.time()
        execution_time = end_time - start_time
        results.put(execution_time)
        assert response.status_code == 200
    
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=execute_workflow)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Calculate statistics
    execution_times = list(results.queue)
    avg_time = sum(execution_times) / len(execution_times)
    max_time = max(execution_times)
    
    assert avg_time < 0.3  # Average execution time should be less than 300ms
    assert max_time < 0.5  # Maximum execution time should be less than 500ms
