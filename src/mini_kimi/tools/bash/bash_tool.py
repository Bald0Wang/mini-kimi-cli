import subprocess

class BashTool:
    name = "Bash"
    description = "Execute a shell command on the local machine."
    
    schema = {
        "type": "function",
        "function": {
            "name": "Bash",
            "description": "Execute a shell command. Use this to explore filesystem or run scripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute."
                    }
                },
                "required": ["command"]
            }
        }
    }

    def __call__(self, command: str) -> dict:
        print(f"\033[90m[System] Executing: {command}\033[0m")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            return {
                "stdout": stdout if stdout else "(No output)",
                "stderr": stderr,
                "exit_code": result.returncode,
                "changed_files": []
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Error: Command timed out.",
                "exit_code": 124,
                "changed_files": []
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Error: {str(e)}",
                "exit_code": 1,
                "changed_files": []
            }
