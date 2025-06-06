"""
Component type definitions used across MCP schemas and API endpoints.
These types should match the frontend component types for proper integration.
"""

from enum import Enum

class SpecificComponentType(str, Enum):
    """
    Enum representing different types of MCP components.
    
    These types should match the frontend component types exactly.
    """
    LLM_PROMPT_AGENT = "LLM Prompt Agent"
    PYTHON_SCRIPT = "Python Script"
    JUPYTER_NOTEBOOK = "Jupyter Notebook"
    DATA_PROCESSOR = "Data Processor"
    MODEL_TRAINER = "Model Trainer"
    CUSTOM = "Custom Component"

    def __str__(self) -> str:
        return self.value
