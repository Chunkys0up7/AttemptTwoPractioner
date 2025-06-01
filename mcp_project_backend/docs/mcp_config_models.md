# MCP Config Models

This document describes the configuration models used for different MCP (Modular Control Platform) component types in the backend. These models are implemented as Pydantic classes and are used for validation, serialization, and API schema generation.

## Overview

Each MCP type (e.g., LLM Prompt Agent, Jupyter Notebook, Python Script, Streamlit App, MCP Package) has a dedicated config model. These models ensure that configuration data is strongly typed and validated throughout the system.

## Config Model List

### 1. LLMConfig

```python
class LLMConfig(BaseModel):
    type: Literal["LLM Prompt Agent"] = "LLM Prompt Agent"
    model_name: str
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    top_p: Optional[float] = None
    top_k: Optional[int] = None
```

**Usage:** Used for LLM-based MCPs. Fields correspond to model selection and prompt configuration.

### 2. NotebookConfig

```python
class NotebookConfig(BaseModel):
    type: Literal["Jupyter Notebook"] = "Jupyter Notebook"
    notebook_path_ref: Optional[str] = None
    notebook_cells: Optional[List[Dict[str, str]]] = None
    parameters: Optional[Dict[str, Any]] = None
```

**Usage:** Used for Jupyter Notebook MCPs. Can reference a file or inline cell structure.

### 3. ScriptConfig

```python
class ScriptConfig(BaseModel):
    type: Literal["Python Script", "TypeScript Script"]
    code_content: str
    interpreter: Optional[str] = "python"
```

**Usage:** Used for script-based MCPs. Stores code and interpreter type.

### 4. StreamlitAppConfig

```python
class StreamlitAppConfig(BaseModel):
    type: Literal["Streamlit App"] = "Streamlit App"
    git_repo_url: Optional[str] = None
    main_script_path: Optional[str] = None
    requirements_content: Optional[str] = None
```

**Usage:** Used for Streamlit App MCPs. Stores repo and script info.

### 5. MCPPackageConfig

```python
class MCPPackageConfig(BaseModel):
    type: Literal["MCP"] = "MCP"
    mcp_configuration: str
```

**Usage:** Used for MCPs that are themselves packages. Stores configuration as a string (JSON or YAML).

## Discriminated Union: MCPConfigPayload

All config models are combined in a discriminated union:

```python
MCPConfigPayload = Union[
    LLMConfig,
    NotebookConfig,
    ScriptConfig,
    StreamlitAppConfig,
    MCPPackageConfig
]
```

## Example Usage in API

- When creating or updating an MCP, the `config` field in the API request/response uses one of these models, validated by FastAPI.
- The backend stores the config as JSONB in the database and deserializes it into the correct model using the `type` discriminator.

## Example API Request

```json
{
  "name": "My LLM Agent",
  "mcp_type": "LLM Prompt Agent",
  "config": {
    "type": "LLM Prompt Agent",
    "model_name": "gpt-4",
    "system_prompt": "You are a helpful assistant.",
    "temperature": 0.7,
    "max_tokens": 1024
  }
}
```

## Extending Config Models

To add a new MCP type, define a new Pydantic config model with a unique `type` field and add it to the `MCPConfigPayload` union.
