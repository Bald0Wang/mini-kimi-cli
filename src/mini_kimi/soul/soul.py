import json
import platform
from typing import List, Dict, Any
from ..llm.client import LLMClient
from ..tools.bash.bash_tool import BashTool
from ..tools.file.write_tool import WriteFileTool
from ..tools.web.search_tool import SearchWebTool, FetchURLTool

class Soul:
    """
    KimiSoul 的简化版。
    """
    def __init__(self):
        self.llm = LLMClient()
        self.tools = [BashTool(), WriteFileTool(), SearchWebTool(), FetchURLTool()]
        self.tool_map = {t.name: t for t in self.tools}
        
        os_info = f"{platform.system()} {platform.release()}"
        
        self.messages: List[Dict[str, Any]] = [
            {
                "role": "system", 
                "content": f"""You are Kimi, a helpful CLI assistant running on {os_info}.
You have access to the following tools:
- Bash: Execute shell commands (Windows PowerShell/CMD).
- WriteFile: Write content to a file.
- SearchWeb: Search the internet for information (DuckDuckGo).
- FetchURL: Read the content of a specific web page.

Rules for Web Browsing:
1. You can search for information using SearchWeb. **Limit to top 3 results per query.**
2. If you need more details from a search result, use FetchURL to read the page.
3. You can follow links found in pages, BUT **do not go deeper than 3 levels** from your initial search.
4. Try at most 3 different search queries if the first one fails.
5. Always summarize what you found.
"""
            }
        ]

    @staticmethod
    def _format_tool_result(result: Any) -> str:
        """
        标准化工具结果为字符串，便于写入 tool 消息。
        目标结构：stdout / stderr / exit_code / changed_files
        """
        if isinstance(result, dict):
            payload = {
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "exit_code": result.get("exit_code", 0),
                "changed_files": result.get("changed_files", []),
            }
            return json.dumps(payload, ensure_ascii=False)
        return str(result)

    def run(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})

        step = 0
        while step < 15:
            step += 1
            
            print(f"\033[94m[Thinking...]\033[0m")
            try:
                response_msg = self.llm.chat(self.messages, self.tools)
            except Exception as e:
                print(f"[Fatal Error] {e}")
                return
            
            self.messages.append(response_msg)

            if response_msg.tool_calls:
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    args_str = tool_call.function.arguments
                    call_id = tool_call.id
                    
                    print(f"\033[32m[Tool Call] {func_name}({args_str})\033[0m")

                    result = ""
                    if func_name in self.tool_map:
                        tool_inst = self.tool_map[func_name]
                        try:
                            args = json.loads(args_str)
                            if func_name == "Bash":
                                result = tool_inst(args.get("command", ""))
                            elif func_name == "WriteFile":
                                result = tool_inst(args.get("path", ""), args.get("content", ""))
                            elif func_name == "SearchWeb":
                                result = tool_inst(args.get("query", ""))
                            elif func_name == "FetchURL":
                                result = tool_inst(args.get("url", ""))
                            else:
                                result = f"Error: Tool logic for {func_name} not implemented."
                        except Exception as e:
                            result = {
                                "stdout": "",
                                "stderr": f"Error executing tool: {e}",
                                "exit_code": 1,
                                "changed_files": []
                            }
                    else:
                        result = {
                            "stdout": "",
                            "stderr": f"Error: Tool {func_name} not found.",
                            "exit_code": 1,
                            "changed_files": []
                        }

                    result_str = self._format_tool_result(result)
                    if len(result_str) > 1000:
                        result_str = result_str[:1000] + "... (truncated)"
                    
                    print(f"\033[90m[Tool Result] {result_str[:100]}...\033[0m")

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": func_name,
                        "content": result_str
                    })
                continue
            else:
                print(f"\n\033[1;37mKimi:\033[0m {response_msg.content}")
                return

        print("[System] Max steps reached.")
