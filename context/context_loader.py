import os

def read_file(file_path: str) -> str:
    """Reads the full content of a file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def chunk_text(text: str, max_tokens: int = 1000) -> list:
    """Chunks text to fit into context length."""
    lines = text.splitlines()
    chunks, current_chunk = [], []
    token_count = 0

    for line in lines:
        line_tokens = len(line.split())
        if token_count + line_tokens > max_tokens:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            token_count = line_tokens
        else:
            current_chunk.append(line)
            token_count += line_tokens

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks
