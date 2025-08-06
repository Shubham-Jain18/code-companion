import os

def list_files(directory: str = '.') -> str:
    """Lists all files and directories in a given directory."""
    try:
        files = os.listdir(directory)
        if not files:
            return "The directory is empty."
        return "\n".join(files)
    except FileNotFoundError:
        return f"Error: The directory '{directory}' was not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def final_answer(answer: str) -> str:
    """A tool to provide the final answer directly to the user."""
    return answer

def read_file(filepath: str) -> str:
    """Reads the content of a specified file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: The file '{filepath}' was not found."
    except Exception as e:
        return f"An unexpected error occurred while reading the file: {e}"

def write_file(filepath: str, content: str) -> str:
    return "Error: write_file tool is not yet implemented."