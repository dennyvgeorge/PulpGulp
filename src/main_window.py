import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSpinBox, QPlainTextEdit, QFileDialog,
    QSizePolicy, QApplication, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent, QDesktopServices
from src.styles import (
    get_stylesheet, get_drop_zone_style, get_toggle_style,
    get_mode_toggle_style, get_file_bar_style,
    get_warning_overlay_style, get_warning_card_style,
    DARK_VOID, LIQUID_LAVA, ACCENT, GLUON_GREY,
    SLATE_GREY, DUSTY_GREY, SNOW, GREEN_DOT, RED_DOT,
    FONT_FAMILY, MONO_FONT
)
from src.worker import CondenseWorker
from src.api_client import check_connection
from src.chunker import read_file, get_file_stats, format_size, estimate_chunks


def resource_path(filename):
    import sys
    if getattr(sys, '_MEIPASS', None):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", filename)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PulpGulp")
        self.setMinimumSize(700, 900)
        self.resize(750, 960)
        self.setStyleSheet(get_stylesheet())
        self.setAcceptDrops(True)

        self.file_content = ""
        self.file_path = ""
        self.mode = "file"
        self.level = "normal"
        self.worker = None
        self.condensed_output = ""
        self.saved_file_path = ""
        self.is_connected = False
        self.model_name = ""

        self.progress_target = 0.0
        self.progress_current = 0.0
        self.progress_timer = QTimer()
        self.progress_timer.setInterval(80)
        self.progress_timer.timeout.connect(self._tick_progress)

        self.setup_ui()
        self.set_state_idle()

        self.connection_timer = QTimer()
        self.connection_timer.setInterval(10000)
        self.connection_timer.timeout.connect(self.check_api_connection)
        self.connection_timer.start()
        QTimer.singleShot(500, self.check_api_connection)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(28, 24, 28, 20)
        self.main_layout.setSpacing(0)

        self._build_header()
        self._add_spacer(43)
        self._build_stats_line()
        self._add_spacer(6)
        self._build_input_area()
        self._add_spacer(16)
        self._build_level_toggle()
        self._add_spacer(16)
        self._build_config_bar()
        self._add_spacer(53)
        self._build_action_button()
        self._add_spacer(4)
        self._build_progress_section()
        self._add_spacer(28)
        self._build_output_area()
        self._add_spacer(6)
        self._build_output_stats()
        self._add_spacer(34)
        self._build_bottom_buttons()
        self._build_warning_overlay()

    def _add_spacer(self, height):
        spacer = QWidget()
        spacer.setFixedHeight(height)
        spacer.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(spacer)

    # ── HEADER ───────────────────────────────────────────────────────────

    def _build_header(self):
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(0)

        self.logo_label = QLabel()
        logo_path = resource_path("logo_header.png")
        if os.path.isfile(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaledToHeight(70, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled)
        else:
            self.logo_label.setText("pulp\ngulp")
            self.logo_label.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Black))
            self.logo_label.setStyleSheet(f"color: {LIQUID_LAVA}; background: transparent;")
        self.logo_label.setFixedHeight(76)
        self.logo_label.setStyleSheet("background: transparent;")
        header.addWidget(self.logo_label)

        header.addStretch()

        mode_container = QWidget()
        mode_container.setStyleSheet("background: transparent;")
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setSpacing(0)
        mode_layout.setContentsMargins(0, 14, 0, 0)

        self.btn_mode_file = QPushButton("Load File")
        self.btn_mode_file.setFixedSize(130, 40)
        self.btn_mode_file.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_file.clicked.connect(lambda: self.set_mode("file"))
        mode_layout.addWidget(self.btn_mode_file)

        self.btn_mode_paste = QPushButton("Paste Text")
        self.btn_mode_paste.setFixedSize(130, 40)
        self.btn_mode_paste.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode_paste.clicked.connect(lambda: self.set_mode("paste"))
        mode_layout.addWidget(self.btn_mode_paste)

        header.addWidget(mode_container)

        header.addStretch()

        self.tagline = QLabel("a vibe coder's friend")
        self.tagline.setObjectName("tagline")
        self.tagline.setStyleSheet(f"color: {DUSTY_GREY}; background: transparent;")
        self.tagline.setContentsMargins(0, 24, 0, 0)
        header.addWidget(self.tagline)

        self.main_layout.addLayout(header)

    # ── STATS LINE ───────────────────────────────────────────────────────

    def _build_stats_line(self):
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)

        self.stat_lines = QLabel("")
        self.stat_lines.setObjectName("statsLabel")
        stats_layout.addWidget(self.stat_lines)

        stats_layout.addStretch()

        self.stat_size = QLabel("")
        self.stat_size.setObjectName("statsLabel")
        stats_layout.addWidget(self.stat_size)

        stats_layout.addStretch()

        self.stat_chunks = QLabel("")
        self.stat_chunks.setObjectName("statsLabel")
        stats_layout.addWidget(self.stat_chunks)

        self.stats_widget = QWidget()
        self.stats_widget.setFixedHeight(20)
        self.stats_widget.setLayout(stats_layout)
        self.main_layout.addWidget(self.stats_widget)

    # ── INPUT AREA ───────────────────────────────────────────────────────

    def _build_input_area(self):
        self.drop_zone = QLabel("Drop a log file here or click to browse")
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setFont(QFont(FONT_FAMILY, 13))
        self.drop_zone.setStyleSheet(get_drop_zone_style())
        self.drop_zone.setFixedHeight(128)
        self.drop_zone.setCursor(Qt.CursorShape.PointingHandCursor)
        self.drop_zone.mousePressEvent = lambda e: self.browse_file()
        self.main_layout.addWidget(self.drop_zone)

        self.file_bar = QWidget()
        self.file_bar.setStyleSheet(get_file_bar_style())
        self.file_bar.setFixedHeight(48)
        fb_layout = QHBoxLayout(self.file_bar)
        fb_layout.setContentsMargins(14, 0, 14, 0)
        fb_layout.setSpacing(10)

        file_icon = QLabel("\u25CF")
        file_icon.setFont(QFont(FONT_FAMILY, 12))
        file_icon.setStyleSheet(f"color: {DUSTY_GREY}; background: transparent;")
        file_icon.setFixedWidth(20)
        fb_layout.addWidget(file_icon)

        self.file_path_label = QLabel("")
        self.file_path_label.setFont(QFont(MONO_FONT, 12))
        self.file_path_label.setStyleSheet(f"color: {SNOW}; background: transparent;")
        fb_layout.addWidget(self.file_path_label, stretch=1)

        self.clear_file_btn = QPushButton("\u2715")
        self.clear_file_btn.setObjectName("clearBtn")
        self.clear_file_btn.setFixedSize(32, 32)
        self.clear_file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_file_btn.clicked.connect(self.clear_file)
        fb_layout.addWidget(self.clear_file_btn)

        self.main_layout.addWidget(self.file_bar)

        self.paste_area = QPlainTextEdit()
        self.paste_area.setObjectName("pasteArea")
        self.paste_area.setPlaceholderText("Paste your log output here...")
        self.paste_area.setFixedHeight(140)
        self.paste_area.textChanged.connect(self.on_paste_text_changed)
        self.main_layout.addWidget(self.paste_area)

    # ── LEVEL TOGGLE ─────────────────────────────────────────────────────

    def _build_level_toggle(self):
        level_container = QWidget()
        level_container.setStyleSheet("background: transparent;")
        level_layout = QHBoxLayout(level_container)
        level_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_layout.setSpacing(4)
        level_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_light = QPushButton("Light")
        self.btn_light.setFixedSize(90, 36)
        self.btn_light.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_light.clicked.connect(lambda: self.set_level("light"))
        level_layout.addWidget(self.btn_light)

        self.btn_normal = QPushButton("Normal")
        self.btn_normal.setFixedSize(90, 36)
        self.btn_normal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_normal.clicked.connect(lambda: self.set_level("normal"))
        level_layout.addWidget(self.btn_normal)

        self.btn_heavy = QPushButton("Heavy")
        self.btn_heavy.setFixedSize(90, 36)
        self.btn_heavy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_heavy.clicked.connect(lambda: self.set_level("heavy"))
        level_layout.addWidget(self.btn_heavy)

        self.main_layout.addWidget(level_container)

    # ── CONFIG BAR ───────────────────────────────────────────────────────

    def _build_config_bar(self):
        config = QHBoxLayout()
        config.setSpacing(12)
        config.setContentsMargins(0, 0, 0, 0)

        self.context_input = QLineEdit()
        self.context_input.setPlaceholderText("e.g. ComfyUI PiD upscale workflow")
        self.context_input.setFixedHeight(40)
        config.addWidget(self.context_input, stretch=35)

        self.chunk_spin = QSpinBox()
        self.chunk_spin.setRange(50, 100000)
        self.chunk_spin.setValue(500)
        self.chunk_spin.setSingleStep(100)
        self.chunk_spin.setSuffix(" lines")
        self.chunk_spin.setFixedHeight(40)
        config.addWidget(self.chunk_spin, stretch=30)

        api_container = QWidget()
        api_container.setStyleSheet("background: transparent;")
        api_layout = QHBoxLayout(api_container)
        api_layout.setContentsMargins(0, 0, 0, 0)
        api_layout.setSpacing(6)

        self.api_url_input = QLineEdit("http://127.0.0.1:1234/v1/chat/completions")
        self.api_url_input.setFont(QFont(MONO_FONT, 10))
        self.api_url_input.setFixedHeight(40)
        api_layout.addWidget(self.api_url_input, stretch=1)

        self.connection_dot = QLabel("\u25CF")
        self.connection_dot.setFont(QFont(FONT_FAMILY, 10))
        self.connection_dot.setStyleSheet(f"color: {DUSTY_GREY}; background: transparent;")
        self.connection_dot.setFixedWidth(16)
        api_layout.addWidget(self.connection_dot)

        self.connection_label = QLabel("")
        self.connection_label.setFont(QFont(FONT_FAMILY, 10))
        self.connection_label.setStyleSheet(f"color: {DUSTY_GREY}; background: transparent;")
        self.connection_label.setFixedWidth(20)
        api_layout.addWidget(self.connection_label)

        config.addWidget(api_container, stretch=35)

        self.main_layout.addLayout(config)

    # ── ACTION BUTTON ────────────────────────────────────────────────────

    def _build_action_button(self):
        btn_container = QHBoxLayout()
        btn_container.setContentsMargins(0, 0, 0, 0)
        btn_container.addStretch(2)

        self.condense_btn = QPushButton("CONDENSE")
        self.condense_btn.setObjectName("condenseBtn")
        self.condense_btn.setFixedHeight(79)
        self.condense_btn.setFixedWidth(307)
        self.condense_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.condense_btn.clicked.connect(self.start_condensing)
        btn_container.addWidget(self.condense_btn, stretch=6)

        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedHeight(79)
        self.stop_btn.setFixedWidth(307)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.clicked.connect(self.stop_condensing)
        btn_container.addWidget(self.stop_btn, stretch=6)

        btn_container.addStretch(2)
        self.main_layout.addLayout(btn_container)

    # ── PROGRESS SECTION ─────────────────────────────────────────────────

    def _build_progress_section(self):
        counter_layout = QHBoxLayout()
        counter_layout.setContentsMargins(0, 0, 0, 2)

        self.chunk_label_left = QLabel("")
        self.chunk_label_left.setObjectName("chunkCounterLeft")
        counter_layout.addWidget(self.chunk_label_left)

        counter_layout.addStretch()

        self.chunk_label_right = QLabel("")
        self.chunk_label_right.setObjectName("chunkCounterRight")
        counter_layout.addWidget(self.chunk_label_right)

        self.main_layout.addLayout(counter_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setFixedHeight(46)
        self.main_layout.addWidget(self.progress_bar)

        spacer_p = QWidget()
        spacer_p.setFixedHeight(4)
        spacer_p.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(spacer_p)

        self.secondary_progress = QProgressBar()
        self.secondary_progress.setObjectName("secondaryProgress")
        self.secondary_progress.setRange(0, 100)
        self.secondary_progress.setValue(0)
        self.secondary_progress.setTextVisible(False)
        self.secondary_progress.setFixedHeight(8)
        self.main_layout.addWidget(self.secondary_progress)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 4, 0, 0)

        self.model_label = QLabel("")
        self.model_label.setObjectName("modelLabel")
        info_layout.addWidget(self.model_label)

        info_layout.addStretch()

        self.eta_label = QLabel("")
        self.eta_label.setObjectName("etaLabel")
        info_layout.addWidget(self.eta_label)

        self.main_layout.addLayout(info_layout)

    # ── OUTPUT AREA ──────────────────────────────────────────────────────

    def _build_output_area(self):
        self.output_terminal = QPlainTextEdit()
        self.output_terminal.setObjectName("outputTerminal")
        self.output_terminal.setReadOnly(True)
        self.output_terminal.setPlaceholderText("// ready to condense")
        self.output_terminal.setMinimumHeight(160)
        self.output_terminal.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.main_layout.addWidget(self.output_terminal, stretch=1)

    # ── OUTPUT STATS ─────────────────────────────────────────────────────

    def _build_output_stats(self):
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)

        self.out_stat_original = QLabel("")
        self.out_stat_original.setObjectName("outputStatsLabel")
        stats_layout.addWidget(self.out_stat_original)

        stats_layout.addStretch()

        self.out_stat_condensed = QLabel("")
        self.out_stat_condensed.setObjectName("outputStatsLabel")
        stats_layout.addWidget(self.out_stat_condensed)

        stats_layout.addStretch()

        self.out_stat_percent = QLabel("")
        self.out_stat_percent.setObjectName("outputStatsLabel")
        stats_layout.addWidget(self.out_stat_percent)

        self.output_stats_widget = QWidget()
        self.output_stats_widget.setFixedHeight(20)
        self.output_stats_widget.setLayout(stats_layout)
        self.main_layout.addWidget(self.output_stats_widget)

    # ── BOTTOM BUTTONS ───────────────────────────────────────────────────

    def _build_bottom_buttons(self):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.setObjectName("wireframeBtn")
        self.copy_btn.setFixedHeight(76)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.copy_btn, stretch=1)

        self.save_btn = QPushButton("Save File")
        self.save_btn.setObjectName("wireframeBtn")
        self.save_btn.setFixedHeight(76)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_file)
        btn_layout.addWidget(self.save_btn, stretch=1)

        self.show_btn = QPushButton("Show in Folder")
        self.show_btn.setObjectName("wireframeBtn")
        self.show_btn.setFixedHeight(76)
        self.show_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_btn.clicked.connect(self.show_in_folder)
        btn_layout.addWidget(self.show_btn, stretch=1)

        self.main_layout.addLayout(btn_layout)

    # ── WARNING OVERLAY ──────────────────────────────────────────────────

    def _build_warning_overlay(self):
        self.warning_overlay = QWidget(self.centralWidget())
        self.warning_overlay.setStyleSheet(get_warning_overlay_style())
        self.warning_overlay.hide()

        overlay_layout = QVBoxLayout(self.warning_overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setStyleSheet(get_warning_card_style())
        card.setFixedWidth(440)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(32, 28, 32, 28)

        dot = QLabel("\u25CF")
        dot.setFont(QFont(FONT_FAMILY, 24))
        dot.setStyleSheet(f"color: {RED_DOT}; background: transparent;")
        dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(dot)

        title = QLabel("Cannot connect to LMStudio at localhost:1234")
        title.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {SNOW}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        card_layout.addWidget(title)

        subtitle = QLabel("Make sure LMStudio is running and a model is loaded")
        subtitle.setFont(QFont(FONT_FAMILY, 11))
        subtitle.setStyleSheet(f"color: {DUSTY_GREY}; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        self.retry_btn = QPushButton("Retry")
        self.retry_btn.setObjectName("retryBtn")
        self.retry_btn.setFixedSize(120, 40)
        self.retry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.retry_btn.clicked.connect(self.retry_connection)
        card_layout.addWidget(self.retry_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        overlay_layout.addWidget(card)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "warning_overlay"):
            self.warning_overlay.setGeometry(self.centralWidget().rect())

    # ── STATE MANAGEMENT ─────────────────────────────────────────────────

    def set_state_idle(self):
        self.stats_widget.hide()
        self.file_bar.hide()
        self.paste_area.hide()
        self.stop_btn.hide()
        self.condense_btn.show()
        self.output_stats_widget.hide()
        self.output_terminal.setPlainText("")
        self.progress_bar.setValue(0)
        self.secondary_progress.setValue(0)
        self.chunk_label_left.setText("")
        self.chunk_label_right.setText("")
        self.model_label.setText("")
        self.eta_label.setText("")
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.show_btn.setEnabled(False)

        if self.mode == "file":
            self.drop_zone.show()
            has_file = bool(self.file_content)
            self.condense_btn.setEnabled(has_file and self.is_connected)
            if has_file:
                self.drop_zone.hide()
                self.file_bar.show()
                self.stats_widget.show()
        else:
            self.drop_zone.hide()
            self.paste_area.show()
            has_text = bool(self.paste_area.toPlainText().strip())
            self.condense_btn.setEnabled(has_text and self.is_connected)
            if has_text:
                self.stats_widget.show()

        self.update_mode_toggle()
        self.update_level_toggle()

    def set_state_processing(self):
        self.condense_btn.hide()
        self.stop_btn.show()
        self.output_terminal.setPlainText("")
        self.output_stats_widget.hide()
        self.copy_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.show_btn.setEnabled(False)
        self.progress_current = 0.0
        self.progress_target = 0.0
        self.progress_bar.setValue(0)
        self.secondary_progress.setValue(0)
        self.progress_timer.start()

    def set_state_complete(self, output):
        self.condensed_output = output
        self.stop_btn.hide()
        self.condense_btn.show()
        self.condense_btn.setEnabled(True)
        self.progress_timer.stop()
        self.progress_bar.setValue(100)
        self.secondary_progress.setValue(100)
        self.eta_label.setText("ETA: 0 minutes")
        self.output_terminal.setPlainText(output)
        self.copy_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

        original_lines = len(self.file_content.splitlines())
        condensed_lines = len(output.splitlines())
        if original_lines > 0:
            reduction = ((original_lines - condensed_lines) / original_lines) * 100
        else:
            reduction = 0

        self.out_stat_original.setText(f"Original: {original_lines:,} Lines")
        self.out_stat_condensed.setText(f"Condensed to: {condensed_lines:,} Lines")
        self.out_stat_percent.setText(f"Condensed by: {reduction:.0f}%")
        self.output_stats_widget.show()

    # ── MODE & LEVEL ─────────────────────────────────────────────────────

    def set_mode(self, mode):
        self.mode = mode
        self.set_state_idle()

    def set_level(self, level):
        self.level = level
        self.update_level_toggle()

    def update_mode_toggle(self):
        self.btn_mode_file.setStyleSheet(get_mode_toggle_style(self.mode == "file", "left"))
        self.btn_mode_paste.setStyleSheet(get_mode_toggle_style(self.mode == "paste", "right"))

    def update_level_toggle(self):
        self.btn_light.setStyleSheet(get_toggle_style(self.level == "light"))
        self.btn_normal.setStyleSheet(get_toggle_style(self.level == "normal"))
        self.btn_heavy.setStyleSheet(get_toggle_style(self.level == "heavy"))

    # ── FILE HANDLING ────────────────────────────────────────────────────

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "",
            "Log Files (*.log *.txt);;All Files (*.*)"
        )
        if path:
            self.load_file(path)

    def load_file(self, path):
        self.file_path = path
        self.file_content = read_file(path)
        line_count, byte_size = get_file_stats(self.file_content)
        chunk_est = estimate_chunks(self.file_content, self.chunk_spin.value())

        self.file_path_label.setText(path)
        self.context_input.setText(os.path.splitext(os.path.basename(path))[0].replace("_", " "))
        self.stat_lines.setText(f"{line_count:,} lines")
        self.stat_size.setText(format_size(byte_size))
        self.stat_chunks.setText(f"{chunk_est} Estimated Chunks")

        self.set_state_idle()

    def clear_file(self):
        self.file_path = ""
        self.file_content = ""
        self.file_path_label.setText("")
        self.condensed_output = ""
        self.saved_file_path = ""
        self.set_state_idle()

    def on_paste_text_changed(self):
        text = self.paste_area.toPlainText()
        if text.strip():
            self.file_content = text
            line_count, byte_size = get_file_stats(text)
            chunk_est = estimate_chunks(text, self.chunk_spin.value())
            self.stat_lines.setText(f"{line_count:,} lines")
            self.stat_size.setText(format_size(byte_size))
            self.stat_chunks.setText(f"{chunk_est} Estimated Chunks")
            self.stats_widget.show()
            self.condense_btn.setEnabled(self.is_connected)
        else:
            self.file_content = ""
            self.stats_widget.hide()
            self.condense_btn.setEnabled(False)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isfile(path):
                self.set_mode("file")
                self.load_file(path)

    # ── CONNECTION CHECK ─────────────────────────────────────────────────

    def check_api_connection(self):
        api_url = self.api_url_input.text().strip()
        connected, model = check_connection(api_url)
        self.is_connected = connected

        if connected:
            self.model_name = model
            self.connection_dot.setStyleSheet(f"color: {GREEN_DOT}; background: transparent;")
            self.connection_label.setText("ok")
            self.connection_label.setStyleSheet(f"color: {GREEN_DOT}; background: transparent;")
            self.warning_overlay.hide()
            has_content = bool(self.file_content)
            self.condense_btn.setEnabled(has_content)
        else:
            self.model_name = ""
            self.connection_dot.setStyleSheet(f"color: {RED_DOT}; background: transparent;")
            self.connection_label.setText("")
            self.connection_label.setStyleSheet(f"color: {RED_DOT}; background: transparent;")
            self.condense_btn.setEnabled(False)

    def retry_connection(self):
        self.check_api_connection()
        if not self.is_connected:
            self.warning_overlay.show()

    def show_warning(self):
        self.warning_overlay.setGeometry(self.centralWidget().rect())
        self.warning_overlay.show()
        self.warning_overlay.raise_()

    # ── CONDENSING ───────────────────────────────────────────────────────

    def start_condensing(self):
        if not self.file_content.strip():
            return

        if not self.is_connected:
            self.show_warning()
            return

        self.set_state_processing()

        if self.model_name:
            self.model_label.setText(f"Model Name: {self.model_name}")

        api_url = self.api_url_input.text().strip()
        context = self.context_input.text().strip()
        chunk_size = self.chunk_spin.value()

        self.worker = CondenseWorker(
            self.file_content, self.level, context, chunk_size, api_url
        )
        self.worker.chunk_started.connect(self.on_chunk_started)
        self.worker.chunk_completed.connect(self.on_chunk_completed)
        self.worker.merge_started.connect(self.on_merge_started)
        self.worker.merge_completed.connect(self.on_merge_completed)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def stop_condensing(self):
        if self.worker:
            self.worker.request_stop()
            self.worker.wait(3000)
            self.worker = None
        self.progress_timer.stop()
        self.stop_btn.hide()
        self.condense_btn.show()
        self.condense_btn.setEnabled(True)

    def on_chunk_started(self, chunk_num, total):
        self.chunk_label_left.setText(f"chunk {chunk_num}/{total}")
        line_count = len(self.file_content.splitlines())
        self.chunk_label_right.setText(f"{line_count:,} lines")
        self.secondary_progress.setValue(int((chunk_num / total) * 100))

    def on_chunk_completed(self, chunk_num, total, result):
        self.progress_target = (chunk_num / total) * 100
        current_text = self.output_terminal.toPlainText()
        separator = f"\n{'=' * 40}\n" if current_text else ""
        self.output_terminal.setPlainText(
            current_text + separator + f"[Chunk {chunk_num}/{total}]\n{result}"
        )
        self.output_terminal.verticalScrollBar().setValue(
            self.output_terminal.verticalScrollBar().maximum()
        )

        eta = self.worker.get_eta_seconds(chunk_num, total) if self.worker else 0
        if eta > 60:
            self.eta_label.setText(f"ETA: {eta / 60:.1f} minutes")
        else:
            self.eta_label.setText(f"ETA: {eta:.0f} seconds")

    def on_merge_started(self):
        self.chunk_label_left.setText("Merging chunks...")
        self.eta_label.setText("")

    def on_merge_completed(self, final_output):
        self.worker = None
        self.set_state_complete(final_output)

    def on_error(self, error_msg):
        self.worker = None
        self.progress_timer.stop()
        self.stop_btn.hide()
        self.condense_btn.show()
        self.condense_btn.setEnabled(True)
        self.output_terminal.setPlainText(f"ERROR: {error_msg}")

        if "Cannot connect" in error_msg:
            self.show_warning()

    # ── SMOOTH PROGRESS ──────────────────────────────────────────────────

    def _tick_progress(self):
        if self.progress_current < self.progress_target:
            diff = self.progress_target - self.progress_current
            step = max(0.3, diff * 0.15)
            self.progress_current = min(self.progress_current + step, self.progress_target)
        elif self.progress_target < 100:
            next_mark = self.progress_target + 5
            if self.progress_current < next_mark:
                self.progress_current += 0.08

        self.progress_bar.setValue(int(self.progress_current))

    # ── OUTPUT ACTIONS ───────────────────────────────────────────────────

    def copy_to_clipboard(self):
        if self.condensed_output:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.condensed_output)
            self.copy_btn.setText("Copied!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy to Clipboard"))

    def save_file(self):
        if not self.condensed_output:
            return

        if self.file_path:
            base, ext = os.path.splitext(self.file_path)
            default_name = f"{base}_condensed.txt"
        else:
            default_name = "condensed_output.txt"

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Condensed Output", default_name,
            "Text Files (*.txt);;All Files (*.*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.condensed_output)
            self.saved_file_path = path
            self.show_btn.setEnabled(True)

    def show_in_folder(self):
        if self.saved_file_path and os.path.isfile(self.saved_file_path):
            directory = os.path.dirname(self.saved_file_path)
            QDesktopServices.openUrl(QUrl.fromLocalFile(directory))
