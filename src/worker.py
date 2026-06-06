import time
from PyQt6.QtCore import QThread, pyqtSignal
from src.condenser import condense_chunk, merge_chunks
from src.chunker import chunk_content, get_file_stats


class CondenseWorker(QThread):
    chunk_started = pyqtSignal(int, int)
    chunk_completed = pyqtSignal(int, int, str)
    merge_started = pyqtSignal()
    merge_completed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_tick = pyqtSignal(float)

    def __init__(self, content, level, context, chunk_size, api_url):
        super().__init__()
        self.content = content
        self.level = level
        self.context = context
        self.chunk_size = chunk_size
        self.api_url = api_url
        self._stop_requested = False
        self.chunk_times = []

    def request_stop(self):
        self._stop_requested = True

    def run(self):
        try:
            chunks = chunk_content(self.content, self.chunk_size)
            total_chunks = len(chunks)

            if total_chunks == 0:
                self.error_occurred.emit("No content to process.")
                return

            condensed_chunks = []

            for i, chunk_text in enumerate(chunks):
                if self._stop_requested:
                    return

                chunk_num = i + 1
                self.chunk_started.emit(chunk_num, total_chunks)

                start_time = time.time()
                result = condense_chunk(
                    chunk_text, chunk_num, total_chunks,
                    self.level, self.context, self.api_url
                )
                elapsed = time.time() - start_time
                self.chunk_times.append(elapsed)

                condensed_chunks.append(result)

                base_progress = (chunk_num / total_chunks) * 100
                self.progress_tick.emit(base_progress)
                self.chunk_completed.emit(chunk_num, total_chunks, result)

            if self._stop_requested:
                return

            if total_chunks > 1:
                self.merge_started.emit()
                final = merge_chunks(condensed_chunks, self.api_url)
                self.merge_completed.emit(final)
            else:
                self.merge_completed.emit(condensed_chunks[0])

        except Exception as e:
            self.error_occurred.emit(str(e))

    def get_eta_seconds(self, current_chunk, total_chunks):
        if not self.chunk_times:
            return 0
        avg_time = sum(self.chunk_times) / len(self.chunk_times)
        remaining = total_chunks - current_chunk
        return avg_time * remaining
