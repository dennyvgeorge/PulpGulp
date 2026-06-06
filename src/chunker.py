import os


def detect_encoding(filepath):
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                f.read(4096)
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return "utf-8"


def read_file(filepath):
    enc = detect_encoding(filepath)
    with open(filepath, "r", encoding=enc, errors="replace") as f:
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
    chunk_lines = []
    for line in content.splitlines():
        chunk_lines.append(line)
        if len(chunk_lines) >= chunk_size:
            yield "\n".join(chunk_lines)
            chunk_lines = []
    if chunk_lines:
        yield "\n".join(chunk_lines)


def chunk_file(filepath, chunk_size=500):
    enc = detect_encoding(filepath)
    chunk_lines = []
    with open(filepath, "r", encoding=enc, errors="replace") as f:
        for line in f:
            chunk_lines.append(line.rstrip("\n"))
            if len(chunk_lines) >= chunk_size:
                yield "\n".join(chunk_lines)
                chunk_lines = []
    if chunk_lines:
        yield "\n".join(chunk_lines)


def estimate_chunks(content, chunk_size=500):
    line_count = len(content.splitlines())
    if line_count == 0:
        return 0
    return (line_count + chunk_size - 1) // chunk_size
