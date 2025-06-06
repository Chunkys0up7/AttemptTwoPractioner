"""
Typed Pydantic models for MCP configurations.

This module defines the specific configuration structures for different MCP types,
allowing for type-safe handling and validation of MCP configurations.
"""
from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, Dict, Union, Literal, List, Any

# --- Individual MCP Type Configuration Models ---


class LLMConfig(BaseModel):
    """Configuration for an 'LLM Prompt Agent' MCP."""
    type: Literal["LLM Prompt Agent"] = Field(
        default="LLM Prompt Agent", description="Discriminator for the LLM Prompt Agent type.")
    model_name: str = Field(
        ..., description="The name or identifier of the LLM model to be used (e.g., 'gpt-3.5-turbo').", alias="model")
    system_prompt: Optional[str] = Field(
        default=None, description="The system prompt to guide the LLM's behavior.", alias="systemPrompt")
    user_prompt_template: Optional[str] = Field(
        default=None, description="Template for the user prompt, may contain placeholders.", alias="userPromptTemplate")
    temperature: Optional[float] = Field(
        default=0.7, ge=0.0, le=2.0, description="Controls randomness. Lower is more deterministic.")
    max_tokens: Optional[int] = Field(
        default=1024, gt=0, description="Maximum number of tokens to generate.", alias="maxTokens")
    top_p: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Nucleus sampling parameter.", alias="topP")
    top_k: Optional[int] = Field(
        default=None, gt=0, description="Top-k sampling parameter.", alias="topK")


class NotebookConfig(BaseModel):
    """Configuration for a 'Jupyter Notebook' MCP."""
    type: Literal["Jupyter Notebook"] = Field(
        default="Jupyter Notebook", description="Discriminator for the Jupyter Notebook type.")
    # Option 1: Reference to a notebook file (e.g., in a Git repo or object store)
    notebook_path_ref: Optional[str] = Field(
        default=None, description="Path or reference to the .ipynb notebook file.")
    # Option 2: Store notebook cell structure directly (as per frontend types.ts)
    notebook_cells: Optional[List[Dict[str, str]]] = Field(
        default=None, description="List of notebook cells, each with id, type (code/markdown), content.", alias="notebookCells")
    parameters: Optional[Dict[str, Any]] = Field(
        default=None, description="Parameters to be passed to the notebook at execution time (e.g., via papermill).")

    @field_validator('notebook_path_ref', 'notebook_cells')
    @classmethod
    def check_notebook_source(cls, v, values):
        # Basic validation: ensure at least one source (path or cells) is provided if the other isn't.
        # More complex validation could be added, e.g. if both are provided, which one takes precedence.
        # This is a simplified example.
        # Pydantic v2: `values` is a `ValidationInfo` object, access data via `values.data`
        # For simplicity, let's assume it works as a dict for this validator for now
        # or that we only check the current field `v` and not cross-field directly here without more setup.
        return v


class ScriptConfig(BaseModel):
    """Configuration for a 'Python Script' or 'TypeScript Script' MCP."""
    # Using a Union of Literals for the type discriminator field
    type: Literal["Python Script", "TypeScript Script"] = Field(
        description="Discriminator for Script types (Python or TypeScript).")
    code_content: str = Field(
        ..., description="The actual source code of the script.", alias="codeContent")
    # 'interpreter' could be implicitly determined by 'type' on the backend, or explicitly set.
    interpreter: Optional[str] = Field(
        default=None, description="Interpreter to use (e.g., 'python3', 'node'). May be inferred from type.")

    @validator('interpreter', pre=True, always=True)
    @classmethod
    def set_default_interpreter(cls, v, values):
        if v is None and 'type' in values:
            if values['type'] == "Python Script":
                return "python"
            elif values['type'] == "TypeScript Script":
                return "node"  # Assuming ts-node or similar execution path
        return v


class StreamlitAppConfig(BaseModel):
    """Configuration for a 'Streamlit App' MCP."""
    type: Literal["Streamlit App"] = Field(
        default="Streamlit App", description="Discriminator for Streamlit App type.")
    git_repo_url: Optional[str] = Field(
        default=None, description="URL of the Git repository containing the Streamlit app.", alias="gitRepoUrl")
    main_script_path: Optional[str] = Field(
        default=None, description="Path to the main Streamlit Python script within the repository.", alias="mainScriptPath")
    # Using 'requirements_content' to align with BACKEND_ENHANCEMENTS.MD, matching frontend 'requirements'
    requirements_content: Optional[str] = Field(
        default=None, description="Content of the requirements.txt file for the Streamlit app.", alias="requirements")
    # Could also have a 'requirements_path_ref' if requirements are stored as a file in the repo


class MCPPackageConfig(BaseModel):
    """Configuration for an 'MCP' (meta-component/package) type."""
    type: Literal["MCP"] = Field(
        default="MCP", description="Discriminator for MCP package type.")
    # This would likely be the ID or a resolvable reference to another MCPDefinition or MCPVersion
    # Storing as a string for now, could be a more structured reference.
    mcp_configuration: str = Field(
        ..., description="Configuration defining the packaged MCP, potentially JSON/YAML string or reference ID.", alias="mcpConfiguration")

# --- Union of all MCP Configuration Payloads ---


# This Union allows FastAPI to correctly validate and deserialize
# the `config` field based on the `type` discriminator.
MCPConfigPayload = Union[
    LLMConfig,
    NotebookConfig,
    ScriptConfig,
    StreamlitAppConfig,
    MCPPackageConfig
]

# --- Helper function for parsing ---


def parse_mcp_config(config_data: Dict[str, Any], mcp_type_str: str) -> MCPConfigPayload:
    """
    Parses a dictionary into the appropriate MCP Pydantic configuration model.

    Args:
        config_data: The raw configuration data as a dictionary.
        mcp_type_str: The string representation of the MCP type, used to ensure
                      the 'type' discriminator is present for Pydantic.

    Returns:
        A Pydantic model instance corresponding to the MCP type.

    Raises:
        ValueError: If the mcp_type_str is unknown or if validation fails.
    """
    if not isinstance(config_data, dict):
        raise ValueError("config_data must be a dictionary.")

    # Ensure the 'type' field is present in the config_data dictionary, matching mcp_type_str.
    # Pydantic's discriminated union relies on this field.
    if 'type' not in config_data:
        config_data['type'] = mcp_type_str
    elif config_data['type'] != mcp_type_str:
        # This case should ideally be caught by frontend or API layer before DB storage,
        # but good to have a check here during parsing from DB.
        raise ValueError(
            f"Mismatch between provided mcp_type_str '{mcp_type_str}' and 'type' in config_data '{config_data['type']}'."
        )

    # Pydantic v2: model_validate is used instead of parse_obj_as
    # The Union type itself can be used for validation with discriminated unions.
    try:
        # Create a temporary model that only contains the relevant type for validation
        # This helps Pydantic resolve the correct model in the Union more reliably if 'type' is present.
        if mcp_type_str == "LLM Prompt Agent":
            return LLMConfig.model_validate(config_data)
        elif mcp_type_str == "Jupyter Notebook":
            return NotebookConfig.model_validate(config_data)
        elif mcp_type_str == "Python Script" or mcp_type_str == "TypeScript Script":
            return ScriptConfig.model_validate(config_data)
        elif mcp_type_str == "Streamlit App":
            return StreamlitAppConfig.model_validate(config_data)
        elif mcp_type_str == "MCP":
            return MCPPackageConfig.model_validate(config_data)
        else:
            raise ValueError(f"Unknown MCP type for parsing: {mcp_type_str}")
    except Exception as e:  # Catch PydanticValidationError or other issues
        # Log the error e for debugging
        raise ValueError(
            f"Failed to parse MCP configuration for type '{mcp_type_str}': {e}")


# Example Usage (for testing or understanding):
if __name__ == "__main__":
    llm_data = {
        "model": "gemini-pro",
        "systemPrompt": "You are a helpful assistant.",
        # type will be added by parse_mcp_config or should be present
    }
    parsed_llm = parse_mcp_config(llm_data, "LLM Prompt Agent")
    print(f"Parsed LLM Config: {parsed_llm.model_dump_json(indent=2)}")

    script_data_python = {"codeContent": "print('Hello Python')"}
    parsed_script_py = parse_mcp_config(script_data_python, "Python Script")
    print(
        f"Parsed Python Script Config: {parsed_script_py.model_dump_json(indent=2)}")
    assert parsed_script_py.interpreter == "python"

    script_data_ts = {
        "codeContent": "console.log('Hello TypeScript')", "type": "TypeScript Script"}
    parsed_script_ts = parse_mcp_config(script_data_ts, "TypeScript Script")
    print(
        f"Parsed TypeScript Script Config: {parsed_script_ts.model_dump_json(indent=2)}")
    assert parsed_script_ts.interpreter == "node"

    notebook_data = {
        "notebookCells": [{"id": "1", "type": "code", "content": "print(1+1)"}],
        # "type": "Jupyter Notebook" # Will be added by parse_mcp_config
    }
    parsed_notebook = parse_mcp_config(notebook_data, "Jupyter Notebook")
    print(
        f"Parsed Notebook Config: {parsed_notebook.model_dump_json(indent=2)}")
