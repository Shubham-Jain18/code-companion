import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

def search_web(query: str) -> str:
    """Searches a curated list of developer websites using Google Programmable Search Engine."""
    try:
        load_dotenv()
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")

        if not api_key or not search_engine_id:
            return "Error: Google Search API key or Search Engine ID is not configured in the .env file."

        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=search_engine_id, num=5).execute()

        if 'items' not in res:
            return "No results found."

        # Format the results into a readable string
        formatted_results = ""
        for item in res['items']:
            formatted_results += f"Title: {item.get('title')}\n"
            formatted_results += f"Link: {item.get('link')}\n"
            formatted_results += f"Snippet: {item.get('snippet')}\n\n"
        return formatted_results

    except Exception as e:
        return f"An unexpected error occurred during the web search: {e}"

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
    """Writes content to a file, asking for user confirmation first."""
    try:
        print(f"ATTENTION: You are about to write the following content to '{filepath}':")
        print("-" * 20)
        print(content)
        print("-" * 20)
        
        confirmation = input("Do you want to proceed? (y/n): ")
        if confirmation.lower() != 'y':
            return "Operation cancelled by user."
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote content to '{filepath}'."
    except Exception as e:
        return f"An unexpected error occurred while writing to the file: {e}"
    
def search_code(query: str, directory: str = ".") -> str:
    """
    Recursively searches for a string in all files within a directory.
    Returns a formatted string of matches (File:LineNumber:Content).
    """
    matches = []
    try:
        for root, _, files in os.walk(directory):
            if ".git" in root or ".venv" in root or "__pycache__" in root:
                continue # Skip common junk directories
            
            for file in files:
                if file.endswith(('.pyc', '.db', '.png', '.jpg')): 
                    continue # Skip binary/irrelevant files
                
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if query in line:
                                # Clean up whitespace for display
                                matches.append(f"{filepath}:{i+1}: {line.strip()}")
                except Exception:
                    continue # Skip files we can't read
        
        if not matches:
            return f"No matches found for '{query}'."
        
        # Return top 50 matches to save tokens
        return "\n".join(matches[:50])
    except Exception as e:
        return f"Error searching code: {e}"