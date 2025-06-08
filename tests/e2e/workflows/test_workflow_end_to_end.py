"""
End-to-end test suite for workflow functionality.

This module contains comprehensive E2E tests for the complete workflow lifecycle,
covering integration between frontend and backend components.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

@pytest.fixture(scope="module")
def browser():
    """Initialize and configure the browser for E2E tests."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="module")
def test_app():
    """Start the test application."""
    from mcp_project_frontend import create_app
    app = create_app(testing=True)
    app.config['TESTING'] = True
    return app

@pytest.fixture(scope="module")
def test_client(test_app):
    """Create a test client for the frontend application."""
    return test_app.test_client()

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.slow
def test_complete_workflow_lifecycle(browser, test_client):
    """Test complete workflow lifecycle from creation to execution."""
    # 1. Login (if authentication is enabled)
    browser.get("http://localhost:3000/login")
    email_input = browser.find_element(By.ID, "email")
    password_input = browser.find_element(By.ID, "password")
    login_button = browser.find_element(By.ID, "login-button")
    
    email_input.send_keys("test@example.com")
    password_input.send_keys("password123")
    login_button.click()
    
    # 2. Create new workflow
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "new-workflow-button"))
    ).click()
    
    # 3. Add components
    component_types = ["input", "filter", "output"]
    for component_type in component_types:
        component_button = browser.find_element(By.ID, f"add-{component_type}")
        component_button.click()
        
    # 4. Connect components
    connections = [
        ("input1", "filter1"),
        ("filter1", "output1")
    ]
    for source, target in connections:
        source_element = browser.find_element(By.ID, f"{source}-output")
        target_element = browser.find_element(By.ID, f"{target}-input")
        # Simulate drag and drop
        source_element.click()
        target_element.click()
    
    # 5. Configure components
    for component in component_types:
        config_button = browser.find_element(By.ID, f"{component}-config")
        config_button.click()
        # Wait for modal to appear
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "config-modal"))
        )
        # Set configuration values
        config_input = browser.find_element(By.ID, f"{component}-config-value")
        config_input.send_keys(f"Test {component} config")
        save_button = browser.find_element(By.ID, "save-config")
        save_button.click()
    
    # 6. Save workflow
    save_button = browser.find_element(By.ID, "save-workflow")
    save_button.click()
    
    # 7. Test workflow execution
    execute_button = browser.find_element(By.ID, "execute-workflow")
    execute_button.click()
    
    # 8. Verify execution results
    result_element = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.ID, "execution-result"))
    )
    assert "Success" in result_element.text
    
    # 9. Verify API response
    response = test_client.get("/api/workflows/1")
    assert response.status_code == 200
    workflow_data = response.json()
    assert workflow_data["name"] == "Test Workflow"
    
    # 10. Clean up
    delete_button = browser.find_element(By.ID, "delete-workflow")
    delete_button.click()
    confirm_delete = browser.find_element(By.ID, "confirm-delete")
    confirm_delete.click()

@pytest.mark.e2e
@pytest.mark.performance
def test_workflow_performance(browser, test_client):
    """Test workflow performance under load."""
    # Create multiple workflows
    num_workflows = 10
    for i in range(num_workflows):
        response = test_client.post(
            "/api/workflows",
            json={
                "name": f"Performance Test {i}",
                "description": "Performance test workflow",
                "components": [
                    {
                        "type": "input",
                        "name": f"input{i}",
                        "properties": {
                            "label": f"Input {i}"
                        }
                    }
                ]
            }
        )
        assert response.status_code == 201
    
    # Measure list performance
    start_time = time.time()
    response = test_client.get("/api/workflows")
    end_time = time.time()
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should take less than 1 second
    
    # Measure execution performance
    workflow_id = response.json()["id"]
    start_time = time.time()
    response = test_client.post(f"/api/workflows/{workflow_id}/execute")
    end_time = time.time()
    assert response.status_code == 200
    assert (end_time - start_time) < 2.0  # Should take less than 2 seconds

@pytest.mark.e2e
@pytest.mark.accessibility
def test_workflow_accessibility(browser):
    """Test workflow builder accessibility."""
    browser.get("http://localhost:3000/workflow-builder")
    
    # Check ARIA labels
    aria_labels = browser.find_elements(By.XPATH, "//*[@aria-label]")
    assert len(aria_labels) > 0
    
    # Check keyboard navigation
    keyboard_nav = browser.find_element(By.ID, "keyboard-nav-test")
    keyboard_nav.send_keys("Tab")
    assert keyboard_nav.get_attribute("tabindex") == "0"
    
    # Check color contrast
    elements = browser.find_elements(By.CSS_SELECTOR, "*")
    for element in elements:
        if element.is_displayed():
            color = element.value_of_css_property("color")
            background = element.value_of_css_property("background-color")
            # Add actual contrast checking logic here
            assert color != background  # Basic check
    
    # Check screen reader support
    sr_elements = browser.find_elements(By.XPATH, "//*[@role]")
    assert len(sr_elements) > 0
