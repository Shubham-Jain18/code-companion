import tools

class Executor:
    """
    The Executor is responsible for taking a single step of a plan
    and executing it.
    """
    def __init__(self, context_manager=None):
        self.context_manager = context_manager
        
        # Standard tools from tools.py
        # All the tools are stateless
        self.tool_map = {
            "search_web": tools.search_web,
            "list_files": tools.list_files,
            "read_file": tools.read_file,
            "write_file": tools.write_file,
            "search_code": tools.search_code,
            "final_answer": tools.final_answer,
        }

    """ 
    Add to Context tool is added here instead of tools.py because this is a stateful tool.
    All the tools in tools.py are stateless.
    """
    def add_to_context(self, filepath: str) -> str:
        """Tool to explicitly add a file to the context window."""
        if not self.context_manager:
            return "Error: Context Manager not available."
        
        try:
            self.context_manager.add_file(filepath)
            return f"Successfully added {filepath} to context."
        except Exception as e:
            return f"Error adding file to context: {e}"

    def execute_step(self, step: dict) -> str:
        """Executes one step of the plan."""
        try:
            tool_name = step.get("tool_to_use")
            parameters = step.get("parameters", {})

            # Special handling for Context Tool (since it needs instance access)
            if tool_name == "add_to_context":
                return self.add_to_context(**parameters)

            if tool_name not in self.tool_map:
                return f"Error: Unknown tool '{tool_name}'."

            tool_function = self.tool_map[tool_name]
            
            # Call the tool function with its parameters
            observation = tool_function(**parameters)
            return observation
        except Exception as e:
            return f"Error during execution of step '{step.get('description')}': {e}"