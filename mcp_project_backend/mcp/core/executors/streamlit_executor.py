from .base_executor import BaseExecutor
from mcp.core.mcp_configs import StreamlitAppConfig
from typing import Dict, Any

class StreamlitExecutor(BaseExecutor):
    """
    Concrete executor for MCPs of type 'Streamlit App'.
    For now, this executor provides metadata about an externally managed Streamlit app.
    """
    async def execute(self, config: StreamlitAppConfig, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a Streamlit MCP configuration and returns informational metadata.
        Args:
            config (StreamlitAppConfig): The configuration for the Streamlit MCP.
            inputs (Dict[str, Any]): Input values (not used for informational approach).
        Returns:
            Dict[str, Any]: Metadata about the Streamlit app.
        """
        await self._log_message(config.type, f"Handling Streamlit App: {getattr(config, 'git_repo_url', None) or 'local content'}")

        if not isinstance(config, StreamlitAppConfig):
            raise TypeError("Configuration for StreamlitExecutor must be StreamlitAppConfig.")

        output_data = {
            "status": "Information Provided",
            "app_type": "Streamlit",
            "git_repository": str(config.git_repo_url) if getattr(config, 'git_repo_url', None) else None,
            "main_script": getattr(config, 'main_script_path', None),
            "access_info": "This component describes a Streamlit application. Deploy and access it externally."
        }
        if getattr(config, 'requirements_content', None):
            output_data["requirements_preview"] = config.requirements_content[:200] + "..."

        await self._log_message(config.type, f"Streamlit app information processed: {output_data}")
        return output_data
