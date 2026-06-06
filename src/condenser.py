from src.prompts import PROMPTS, MERGE_PROMPT
from src.api_client import send_to_llm
from src.chunker import chunk_content, get_file_stats


def condense_chunk(chunk_text, chunk_num, total_chunks, level="normal", context="", api_url="http://127.0.0.1:1234/v1/chat/completions"):
    system_prompt = PROMPTS[level]
    if context:
        system_prompt += f"\n\nCONTEXT: This log is from: {context}"
    user_prompt = f"[Chunk {chunk_num}/{total_chunks}]\n\n{chunk_text}"
    return send_to_llm(user_prompt, system_prompt, api_url)


def merge_chunks(condensed_chunks, api_url="http://127.0.0.1:1234/v1/chat/completions"):
    if len(condensed_chunks) == 1:
        return condensed_chunks[0]

    if len(condensed_chunks) <= 15:
        combined = ""
        for i, chunk in enumerate(condensed_chunks):
            combined += f"\n--- Chunk {i + 1} ---\n{chunk}\n"
        return send_to_llm(combined, MERGE_PROMPT, api_url)

    batch_size = 10
    batches = []
    for i in range(0, len(condensed_chunks), batch_size):
        batch = condensed_chunks[i:i + batch_size]
        combined = ""
        for j, chunk in enumerate(batch):
            combined += f"\n--- Chunk {i + j + 1} ---\n{chunk}\n"
        merged_batch = send_to_llm(combined, MERGE_PROMPT, api_url)
        batches.append(merged_batch)

    if len(batches) > 1:
        return merge_chunks(batches, api_url)
    return batches[0]
