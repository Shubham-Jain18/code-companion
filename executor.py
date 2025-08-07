import tools

class Executor:
    """
    The Executor is responsible for taking a single step of a plan
    and executing it by calling the appropriate tool.
    """
    def __init__(self):
        # A mapping from tool names to the actual Python functions
        self.tool_map = {
            "search_web": tools.search_web,
            "list_files": tools.list_files,
            "final_answer": tools.final_answer,
            "read_file": tools.read_file,
            "write_file": tools.write_file,
        }

    def execute_step(self, step: dict) -> str:
        """Executes one step of the plan."""
        try:
            tool_name = step.get("tool_to_use")
            parameters = step.get("parameters", {})

            if tool_name not in self.tool_map:
                return f"Error: Unknown tool '{tool_name}'. Please use one of {list(self.tool_map.keys())}"

            tool_function = self.tool_map[tool_name]
            
            # Call the tool function with its parameters
            observation = tool_function(**parameters)
            return observation
        except Exception as e:
            # General error handling for tool execution
            return f"Error during execution of step '{step.get('description')}': {e}"