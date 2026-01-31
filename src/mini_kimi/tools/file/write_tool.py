class WriteFileTool:
    name = "WriteFile"
    description = "Write content to a file."

    schema = {
        "type": "function",
        "function": {
            "name": "WriteFile",
            "description": "Write content to a file. Overwrites existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to write to."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write."
                    }
                },
                "required": ["path", "content"]
            }
        }
    }

    def __call__(self, path: str, content: str) -> dict:
        print(f"\033[90m[System] Writing to file: {path}\033[0m")
        try:
            if ".." in path:
                return {
                    "stdout": "",
                    "stderr": "Error: Path cannot contain '..'",
                    "exit_code": 1,
                    "changed_files": []
                }
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "stdout": f"Successfully wrote to {path}",
                "stderr": "",
                "exit_code": 0,
                "changed_files": [path]
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Error writing file: {str(e)}",
                "exit_code": 1,
                "changed_files": []
            }
