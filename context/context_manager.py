import os
from context.context_loader import read_file, chunk_text

class ContextManager:
    def __init__(self):
        self.context_files = []  # list of paths
        self.file_contents = {}  # path -> chunks

    def add_file(self, file_path: str):
        """Adds file to context."""
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return

        content = read_file(file_path)
        chunks = chunk_text(content)
        self.context_files.append(file_path)
        self.file_contents[file_path] = chunks

    def clear_context(self):
        self.context_files = []
        self.file_contents = {}

    def get_context(self, max_chunks: int = 3) -> str:
        """Returns context to be used in prompts."""
        selected_chunks = []

        for file_path in self.context_files:
            chunks = self.file_contents.get(file_path, [])
            selected_chunks.extend(chunks[:max_chunks])  # take first N chunks

        return "\n\n---\n\n".join(selected_chunks)
