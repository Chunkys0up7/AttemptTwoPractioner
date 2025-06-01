import subprocess
import tempfile
import os
import json
from typing import Dict, Any
from .base_executor import BaseExecutor
from mcp.core.mcp_configs import ScriptConfig

class ScriptExecutor(BaseExecutor):
    """
    Concrete executor for MCPs of type 'Python Script' or 'TypeScript Script'.
    Executes the script in a subprocess, passing inputs as environment variables.
    """
    async def execute(self, config: ScriptConfig, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a script MCP using the specified configuration and inputs.
        Args:
            config (ScriptConfig): The configuration for the script MCP.
            inputs (Dict[str, Any]): Input values for the script.
        Returns:
            Dict[str, Any]: Output values produced by the script.
        Raises:
            RuntimeError: If the script execution fails.
            TimeoutError: If the script execution times out.
        """
        await self._log_message(config.type, f"Executing Script: type {config.type}")

        if not isinstance(config, ScriptConfig):
            raise TypeError("Configuration for ScriptExecutor must be ScriptConfig.")

        script_content = config.code_content
        interpreter_command = []

        if config.type == "Python Script":
            interpreter_command = ["python"]
            file_extension = ".py"
        elif config.type == "TypeScript Script":
            interpreter_command = ["npx", "ts-node"]
            file_extension = ".ts"
        else:
            raise ValueError(f"Unsupported script type: {config.type}")

        with tempfile.NamedTemporaryFile(mode="w", suffix=file_extension, delete=False) as tmp_script:
            tmp_script.write(script_content)
            script_path = tmp_script.name

        try:
            env = os.environ.copy()
            env["MCP_INPUTS"] = json.dumps(inputs)
            command_to_run = interpreter_command + [script_path]
            await self._log_message(config.type, f"Running command: {' '.join(command_to_run)}")

            process = subprocess.Popen(
                command_to_run,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            stdout, stderr = process.communicate(timeout=config.timeout_seconds or 600)

            if process.returncode != 0:
                error_message = f"Script execution failed with code {process.returncode}.\nStderr: {stderr}\nStdout: {stdout}"
                await self._log_message(config.type, error_message, level="ERROR")
                raise RuntimeError(error_message)

            await self._log_message(config.type, f"Script stdout: {stdout}")
            if stderr:
                await self._log_message(config.type, f"Script stderr: {stderr}", level="WARNING")

            try:
                output_data = json.loads(stdout.strip()) if stdout.strip() else {}
            except json.JSONDecodeError:
                await self._log_message(config.type, "Script output was not valid JSON. Returning raw stdout.", level="WARNING")
                output_data = {"raw_stdout": stdout.strip()}
            return output_data

        except subprocess.TimeoutExpired:
            error_message = f"Script execution timed out after {config.timeout_seconds or 600} seconds."
            await self._log_message(config.type, error_message, level="ERROR")
            raise TimeoutError(error_message)
        except Exception as e:
            await self._log_message(config.type, f"Script execution failed: {e}", level="ERROR")
            raise
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)
