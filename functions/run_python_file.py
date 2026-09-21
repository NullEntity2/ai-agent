import os
import subprocess
from config import *

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        valid_target_dir = os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_path]
        if args:
            command.extend(args)
        process_result = subprocess.run(
            command,
            cwd=os.path.dirname(target_path),
            timeout=PYTHON_TIMEOUT,
            text=True,
            capture_output=True,
        )
        if process_result.returncode != 0:
            return f'Error: Process exited with code {process_result.returncode}'
        output = ""
        if not process_result.stdout and not process_result.stderr:
            output = "Success: No output produced"
        if process_result.stdout:
            output += f"STDOUT: {process_result.stdout}\n"
        if process_result.stderr:
            output += f"STDERR: {process_result.stderr}\n"
        return output

    except Exception as e:
        return f"Error: executing Python file: {e}"