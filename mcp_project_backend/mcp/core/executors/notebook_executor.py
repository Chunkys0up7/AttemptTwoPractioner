import papermill as pm
import nbformat
import os
import tempfile
from typing import Dict, Any
from .base_executor import BaseExecutor
from mcp.core.mcp_configs import NotebookConfig

class NotebookExecutor(BaseExecutor):
    """
    Concrete executor for MCPs of type 'Jupyter Notebook'.
    Executes a notebook using Papermill, supporting both file path and embedded cell content.
    """
    async def execute(self, config: NotebookConfig, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a Jupyter notebook MCP using the specified configuration and inputs.
        Args:
            config (NotebookConfig): The configuration for the notebook MCP.
            inputs (Dict[str, Any]): Input values for the notebook.
        Returns:
            Dict[str, Any]: Output values produced by the notebook.
        Raises:
            RuntimeError: If the notebook execution fails.
        """
        await self._log_message(config.type, f"Executing Jupyter Notebook: {getattr(config, 'notebook_path_ref', None) or 'embedded notebook'}")

        if not isinstance(config, NotebookConfig):
            raise TypeError("Configuration for NotebookExecutor must be NotebookConfig.")

        input_path = None
        output_path = None
        temp_dir = tempfile.mkdtemp()

        try:
            if getattr(config, 'notebook_path_ref', None):
                input_path = config.notebook_path_ref
            elif getattr(config, 'notebook_cells', None):
                temp_notebook = nbformat.v4.new_notebook(cells=[
                    nbformat.v4.new_code_cell(cell['content']) if cell['type'] == 'code'
                    else nbformat.v4.new_markdown_cell(cell['content'])
                    for cell in config.notebook_cells
                ])
                input_path = os.path.join(temp_dir, "temp_notebook.ipynb")
                with open(input_path, 'w', encoding='utf-8') as f:
                    nbformat.write(temp_notebook, f)
            else:
                raise ValueError("Notebook configuration must provide either notebook_path_ref or notebook_cells.")

            output_path = os.path.join(temp_dir, "output_notebook.ipynb")
            await self._log_message(config.type, f"Using input notebook: {input_path}")
            await self._log_message(config.type, f"Parameters: {getattr(config, 'parameters', None) or inputs}")

            execution_parameters = {**(getattr(config, 'parameters', {}) or {}), **inputs}

            pm.execute_notebook(
                input_path=input_path,
                output_path=output_path,
                parameters=execution_parameters,
            )

            await self._log_message(config.type, f"Notebook execution completed. Output at: {output_path}")

            # For demonstration, just return the output notebook path
            return {"output_notebook_path": output_path}

        except Exception as e:
            await self._log_message(config.type, f"Notebook execution failed: {e}", level="ERROR")
            raise
        finally:
            # Clean up temporary files/directory
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
