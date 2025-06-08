"""
Accessibility test suite for the workflow builder UI.
"""
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

@pytest.mark.accessibility
def test_workflow_builder_keyboard_navigation(browser):
    """Test keyboard navigation in workflow builder."""
    browser.get("http://localhost:3000/workflow-builder")
    
    # Wait for page load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "workflow-builder"))
    )
    
    # Test keyboard navigation through components
    component_list = browser.find_element(By.ID, "component-list")
    component_list.send_keys("Tab")  # Focus first component
    
    # Verify focus is properly set
    focused_element = browser.switch_to.active_element
    assert focused_element.get_attribute("tabindex") == "0"
    
    # Test arrow key navigation
    focused_element.send_keys("ArrowDown")  # Move to next component
    next_element = browser.switch_to.active_element
    assert next_element != focused_element
    
    # Test form controls
    form = browser.find_element(By.ID, "component-form")
    form.send_keys("Tab")  # Focus first form field
    form_field = browser.switch_to.active_element
    assert form_field.get_attribute("tabindex") == "0"

@pytest.mark.accessibility
def test_workflow_builder_screen_reader(browser):
    """Test screen reader support in workflow builder."""
    browser.get("http://localhost:3000/workflow-builder")
    
    # Check ARIA labels
    aria_labels = browser.find_elements(By.XPATH, "//*[@aria-label]")
    assert len(aria_labels) > 0
    
    # Check roles
    roles = browser.find_elements(By.XPATH, "//*[@role]")
    assert len(roles) > 0
    
    # Check landmarks
    landmarks = browser.find_elements(By.XPATH, "//main | //nav | //aside")
    assert len(landmarks) > 0
    
    # Check form controls
    form_controls = browser.find_elements(By.XPATH, "//*[@role='button' or @role='checkbox' or @role='radio']")
    assert len(form_controls) > 0

@pytest.mark.accessibility
def test_workflow_builder_color_contrast(browser):
    """Test color contrast in workflow builder."""
    browser.get("http://localhost:3000/workflow-builder")
    
    # Get all visible elements
    elements = browser.find_elements(By.CSS_SELECTOR, "*")
    
    for element in elements:
        if element.is_displayed():
            # Get color values
            color = element.value_of_css_property("color")
            background = element.value_of_css_property("background-color")
            
            # Convert to RGB values
            color_rgb = _convert_color_to_rgb(color)
            background_rgb = _convert_color_to_rgb(background)
            
            # Calculate contrast ratio
            contrast_ratio = _calculate_contrast_ratio(color_rgb, background_rgb)
            
            # WCAG 2.1 AA requires contrast ratio of at least 4.5:1 for normal text
            assert contrast_ratio >= 4.5, f"Element {element.tag_name} has insufficient contrast"

@pytest.mark.accessibility
def test_workflow_builder_form_accessibility(browser):
    """Test form accessibility in workflow builder."""
    browser.get("http://localhost:3000/workflow-builder")
    
    # Check form labels
    labels = browser.find_elements(By.TAG_NAME, "label")
    for label in labels:
        assert label.get_attribute("for") is not None
    
    # Check input fields
    inputs = browser.find_elements(By.CSS_SELECTOR, "input, select, textarea")
    for input_field in inputs:
        assert input_field.get_attribute("aria-label") or input_field.get_attribute("title")
        assert input_field.get_attribute("tabindex") == "0"

@pytest.mark.accessibility
def test_workflow_builder_error_states(browser):
    """Test error states accessibility in workflow builder."""
    browser.get("http://localhost:3000/workflow-builder")
    
    # Trigger validation error
    form = browser.find_element(By.ID, "component-form")
    submit_button = form.find_element(By.CSS_SELECTOR, "[type='submit']")
    submit_button.click()
    
    # Check error messages
    error_messages = browser.find_elements(By.CSS_SELECTOR, ".error-message")
    for error in error_messages:
        assert error.get_attribute("role") == "alert"
        assert error.get_attribute("aria-live") == "polite"

# Helper functions
def _convert_color_to_rgb(color_str: str) -> tuple:
    """Convert CSS color string to RGB tuple."""
    if color_str.startswith("rgb"):
        # Handle rgb(x, y, z) format
        values = color_str.split(",")
        return (
            int(values[0].split("(")[1]),
            int(values[1]),
            int(values[2].split(")")[0])
        )
    elif color_str.startswith("rgba"):
        # Handle rgba(x, y, z, a) format
        values = color_str.split(",")
        return (
            int(values[0].split("(")[1]),
            int(values[1]),
            int(values[2])
        )
    else:
        # Handle hex format
        hex_color = color_str.lstrip("#")
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )

def _calculate_contrast_ratio(color1: tuple, color2: tuple) -> float:
    """Calculate contrast ratio between two colors."""
    def _relative_luminance(rgb: tuple) -> float:
        r, g, b = rgb
        r = (r / 255) ** 2.2
        g = (g / 255) ** 2.2
        b = (b / 255) ** 2.2
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    lum1 = _relative_luminance(color1)
    lum2 = _relative_luminance(color2)
    
    if lum1 > lum2:
        return (lum1 + 0.05) / (lum2 + 0.05)
    else:
        return (lum2 + 0.05) / (lum1 + 0.05)
