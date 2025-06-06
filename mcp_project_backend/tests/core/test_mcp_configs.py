"""
Tests for MCP Pydantic configuration models and parsing logic.
"""
import pytest
import uuid
from pydantic import ValidationError

from mcp.core.mcp_configs import (
    LLMConfig,
    NotebookConfig,
    ScriptConfig,
    StreamlitAppConfig,
    MCPPackageConfig,
    MCPConfigPayload, # For type hinting, though direct instantiation is via specific types
    parse_mcp_config
)
from mcp.db.models import MCPVersion # For testing hybrid property

# --- Test successful parsing and model instantiation ---

def test_llm_config_parsing_valid():
    data = {"model": "gpt-4", "systemPrompt": "Be nice.", "temperature": 0.5}
    parsed = parse_mcp_config(data, "LLM Prompt Agent")
    assert isinstance(parsed, LLMConfig)
    assert parsed.model_name == "gpt-4"
    assert parsed.system_prompt == "Be nice."
    assert parsed.temperature == 0.5
    assert parsed.type == "LLM Prompt Agent"

def test_llm_config_direct_instantiation():
    config = LLMConfig(model="claude-2", maxTokens=2000)
    assert config.model_name == "claude-2"
    assert config.max_tokens == 2000
    assert config.type == "LLM Prompt Agent"
    # Test Pydantic dump with alias
    assert config.model_dump(by_alias=True)["model"] == "claude-2"
    assert config.model_dump(by_alias=True)["maxTokens"] == 2000

def test_notebook_config_parsing_valid_cells():
    data = {"notebookCells": [{"id": "1", "type": "code", "content": "print('hi')"}]}
    parsed = parse_mcp_config(data, "Jupyter Notebook")
    assert isinstance(parsed, NotebookConfig)
    assert parsed.notebook_cells[0]["content"] == "print('hi')"
    assert parsed.type == "Jupyter Notebook"

def test_notebook_config_parsing_valid_path():
    data = {"notebook_path_ref": "/path/to/notebook.ipynb", "parameters": {"alpha": 0.1}}
    parsed = parse_mcp_config(data, "Jupyter Notebook")
    assert isinstance(parsed, NotebookConfig)
    assert parsed.notebook_path_ref == "/path/to/notebook.ipynb"
    assert parsed.parameters["alpha"] == 0.1

def test_script_config_parsing_python():
    data = {"codeContent": "import os"}
    parsed = parse_mcp_config(data, "Python Script")
    assert isinstance(parsed, ScriptConfig)
    assert parsed.code_content == "import os"
    assert parsed.type == "Python Script"
    assert parsed.interpreter == "python"

def test_script_config_parsing_typescript():
    data = {"codeContent": "console.log(1)", "type": "TypeScript Script"} # Type explicitly provided
    parsed = parse_mcp_config(data, "TypeScript Script")
    assert isinstance(parsed, ScriptConfig)
    assert parsed.code_content == "console.log(1)"
    assert parsed.type == "TypeScript Script"
    assert parsed.interpreter == "node"

def test_streamlit_app_config_parsing():
    data = {"gitRepoUrl": "https://some.repo/app.git", "mainScriptPath": "app/run.py", "requirements": "streamlit\npandas"}
    parsed = parse_mcp_config(data, "Streamlit App")
    assert isinstance(parsed, StreamlitAppConfig)
    assert parsed.git_repo_url == "https://some.repo/app.git"
    assert parsed.requirements_content == "streamlit\npandas"
    assert parsed.type == "Streamlit App"

def test_mcp_package_config_parsing():
    data = {"mcpConfiguration": "other_mcp_definition_id_or_json_string"}
    parsed = parse_mcp_config(data, "MCP")
    assert isinstance(parsed, MCPPackageConfig)
    assert parsed.mcp_configuration == "other_mcp_definition_id_or_json_string"
    assert parsed.type == "MCP"

# --- Test parsing failures and validation errors ---

def test_llm_config_missing_required_field():
    data = {"systemPrompt": "Be nice."}
    with pytest.raises(ValueError, match="Failed to parse MCP configuration for type 'LLM Prompt Agent'.*'model'*"):
        parse_mcp_config(data, "LLM Prompt Agent")

def test_script_config_missing_codecontent():
    with pytest.raises(ValueError, match="Failed to parse MCP configuration for type 'Python Script'.*'codeContent'*"):
        parse_mcp_config({}, "Python Script")

def test_unknown_mcp_type_parsing():
    with pytest.raises(ValueError, match="Unknown MCP type for parsing: Unknown Type"):
        parse_mcp_config({}, "Unknown Type")

def test_mismatch_type_in_data_and_arg():
    data = {"type": "Python Script", "codeContent": "print('ok')"}
    with pytest.raises(ValueError, match="Mismatch between provided mcp_type_str 'LLM Prompt Agent' and 'type' in config_data 'Python Script'"):
        parse_mcp_config(data, "LLM Prompt Agent")


# --- Test MCPVersion hybrid property for config ---

def test_mcp_version_config_hybrid_property_get():
    """Test getting the config via the hybrid property."""
    mcp_def_id = uuid.uuid4()
    version_id = uuid.uuid4()
    raw_config_data = {"model": "test-model", "temperature": 0.8}
    
    mcp_ver = MCPVersion(
        id=version_id,
        mcp_definition_id=mcp_def_id,
        version_string="1.0.0",
        mcp_type="LLM Prompt Agent",
        config_payload_data=raw_config_data # Stored as JSONB in DB
    )
    
    # Access the hybrid property
    parsed_config = mcp_ver.config
    assert isinstance(parsed_config, LLMConfig)
    assert parsed_config.model_name == "test-model"
    assert parsed_config.temperature == 0.8
    assert parsed_config.type == "LLM Prompt Agent"

def test_mcp_version_config_hybrid_property_set():
    """Test setting the config via the hybrid property."""
    mcp_def_id = uuid.uuid4()
    version_id = uuid.uuid4()
    
    mcp_ver = MCPVersion(
        id=version_id,
        mcp_definition_id=mcp_def_id,
        version_string="1.0.0",
        mcp_type="Python Script"
    )
    
    new_script_config = ScriptConfig(type="Python Script", codeContent="print('Hello from hybrid property')")
    mcp_ver.config = new_script_config
    
    assert mcp_ver.config_payload_data["codeContent"] == "print('Hello from hybrid property')"
    assert mcp_ver.config_payload_data["type"] == "Python Script"
    assert mcp_ver.config_payload_data["interpreter"] == "python" # Default from model
    
    # Test accessing it back
    retrieved_config = mcp_ver.config
    assert isinstance(retrieved_config, ScriptConfig)
    assert retrieved_config.code_content == "print('Hello from hybrid property')"

def test_mcp_version_config_hybrid_property_set_none():
    mcp_ver = MCPVersion(mcp_type="LLM Prompt Agent", config_payload_data={"model": "old"})
    mcp_ver.config = None
    assert mcp_ver.config_payload_data is None
    assert mcp_ver.config is None

def test_mcp_version_config_setter_type_mismatch():
    mcp_ver = MCPVersion(mcp_type="LLM Prompt Agent")
    wrong_config = ScriptConfig(type="Python Script", codeContent="Oops")
    with pytest.raises(ValueError, match="MCPVersion.mcp_type \('LLM Prompt Agent'\) and new_config.type \('Python Script'\) mismatch"):
        mcp_ver.config = wrong_config

def test_mcp_version_config_getter_parse_error():
    """Test scenario where stored DB data is invalid for the mcp_type."""
    mcp_ver = MCPVersion(
        mcp_type="LLM Prompt Agent", 
        config_payload_data={"invalid_field": "nodata"} # Missing 'model'
    )
    with pytest.raises(ValueError, match="Failed to parse MCP configuration for type 'LLM Prompt Agent'.*'model'*"):
        _ = mcp_ver.config # Access to trigger parsing 