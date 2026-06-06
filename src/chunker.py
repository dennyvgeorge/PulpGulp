import os


def read_file(filepath):
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            return content
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def get_file_stats(content):
    lines = content.splitlines()
    line_count = len(lines)
    byte_size = len(content.encode("utf-8", errors="replace"))
    return line_count, byte_size


def format_size(byte_size):
    if byte_size < 1024:
        return f"{byte_size} B"
    elif byte_size < 1024 * 1024:
        return f"{byte_size / 1024:.1f} KB"
    else:
        return f"{byte_size / (1024 * 1024):.1f} MB"


def chunk_content(content, chunk_size=500):
    lines = content.splitlines()
    chunks = []
    for i in range(0, len(lines), chunk_size):
        chunk_lines = lines[i:i + chunk_size]
        chunks.append("\n".join(chunk_lines))
    return chunks


def estimate_chunks(content, chunk_size=500):
    line_count = len(content.splitlines())
    if line_count == 0:
        return 0
    return (line_count + chunk_size - 1) // chunk_size
