# PulpGulp Color Palette
DARK_VOID = "#151419"
LIQUID_LAVA = "#F56E0F"
GLUON_GREY = "#1B1B1E"
SLATE_GREY = "#262626"
DUSTY_GREY = "#878787"
SNOW = "#FBFBFB"
GREEN_DOT = "#4CAF50"
RED_DOT = "#E53935"

ACCENT = LIQUID_LAVA
ACCENT_HOVER = "#D9620D"
ACCENT_PRESSED = "#C0570C"
SNOW_HOVER = "#E0E0E0"
SNOW_PRESSED = "#C8C8C8"

FONT_FAMILY = "Segoe UI"
MONO_FONT = "Consolas"


def get_stylesheet():
    return f"""
    QMainWindow {{
        background-color: {DARK_VOID};
    }}

    QLabel {{
        color: {SNOW};
        font-family: {FONT_FAMILY};
    }}

    QLabel#tagline {{
        color: {DUSTY_GREY};
        font-size: 11px;
    }}

    QLabel#statsLabel {{
        color: {DUSTY_GREY};
        font-size: 12px;
    }}

    QLabel#chunkCounterLeft {{
        color: {SNOW};
        font-size: 12px;
    }}

    QLabel#chunkCounterRight {{
        color: {SNOW};
        font-size: 12px;
    }}

    QLabel#modelLabel {{
        color: {DUSTY_GREY};
        font-size: 11px;
    }}

    QLabel#etaLabel {{
        color: {DUSTY_GREY};
        font-size: 11px;
    }}

    QLabel#outputStatsLabel {{
        color: {DUSTY_GREY};
        font-size: 12px;
        font-weight: bold;
    }}

    QLineEdit {{
        background-color: {SLATE_GREY};
        color: {SNOW};
        border: 1px solid {ACCENT};
        border-radius: 6px;
        padding: 8px 12px;
        font-family: {FONT_FAMILY};
        font-size: 13px;
    }}

    QLineEdit:focus {{
        border: 1px solid {ACCENT};
    }}

    QSpinBox {{
        background-color: {SLATE_GREY};
        color: {SNOW};
        border: 1px solid {ACCENT};
        border-radius: 6px;
        padding: 8px 28px 8px 12px;
        font-family: {FONT_FAMILY};
        font-size: 13px;
    }}

    QSpinBox::up-button {{
        background-color: transparent;
        border: none;
        width: 18px;
        height: 12px;
        subcontrol-position: top right;
        subcontrol-origin: padding;
        margin-top: 4px;
        margin-right: 6px;
    }}

    QSpinBox::down-button {{
        background-color: transparent;
        border: none;
        width: 18px;
        height: 12px;
        subcontrol-position: bottom right;
        subcontrol-origin: padding;
        margin-bottom: 4px;
        margin-right: 6px;
    }}

    QSpinBox::up-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid {DUSTY_GREY};
        width: 0;
        height: 0;
    }}

    QSpinBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {DUSTY_GREY};
        width: 0;
        height: 0;
    }}

    QSpinBox::up-arrow:hover {{
        border-bottom: 5px solid {ACCENT};
    }}

    QSpinBox::down-arrow:hover {{
        border-top: 5px solid {ACCENT};
    }}

    QPlainTextEdit#outputTerminal {{
        background-color: {GLUON_GREY};
        color: {DUSTY_GREY};
        border: 1px solid {SLATE_GREY};
        border-radius: 8px;
        padding: 12px;
        font-family: {MONO_FONT};
        font-size: 12px;
        selection-background-color: {ACCENT};
    }}

    QPlainTextEdit#pasteArea {{
        background-color: {GLUON_GREY};
        color: {SNOW};
        border: 1px solid {DUSTY_GREY};
        border-radius: 8px;
        padding: 12px;
        font-family: {MONO_FONT};
        font-size: 12px;
    }}

    QPushButton#condenseBtn {{
        background-color: {ACCENT};
        color: {SNOW};
        border: none;
        border-radius: 10px;
        padding: 16px;
        font-family: {FONT_FAMILY};
        font-size: 20px;
        font-weight: bold;
    }}

    QPushButton#condenseBtn:hover {{
        background-color: {ACCENT_HOVER};
    }}

    QPushButton#condenseBtn:pressed {{
        background-color: {ACCENT_PRESSED};
    }}

    QPushButton#condenseBtn:disabled {{
        background-color: {SLATE_GREY};
        color: {DUSTY_GREY};
    }}

    QPushButton#stopBtn {{
        background-color: {SNOW};
        color: {DARK_VOID};
        border: none;
        border-radius: 10px;
        padding: 16px;
        font-family: {FONT_FAMILY};
        font-size: 20px;
        font-weight: bold;
    }}

    QPushButton#stopBtn:hover {{
        background-color: {SNOW_HOVER};
    }}

    QPushButton#stopBtn:pressed {{
        background-color: {SNOW_PRESSED};
    }}

    QPushButton#wireframeBtn {{
        background-color: transparent;
        color: {DUSTY_GREY};
        border: 1px solid {ACCENT};
        border-radius: 8px;
        padding: 12px 20px;
        font-family: {FONT_FAMILY};
        font-size: 13px;
    }}

    QPushButton#wireframeBtn:hover {{
        background-color: {ACCENT};
        color: {SNOW};
    }}

    QPushButton#wireframeBtn:pressed {{
        background-color: {ACCENT_PRESSED};
        color: {SNOW};
    }}

    QPushButton#wireframeBtn:disabled {{
        border: 1px solid {SLATE_GREY};
        color: {SLATE_GREY};
    }}

    QPushButton#clearBtn {{
        background-color: transparent;
        color: {DUSTY_GREY};
        border: none;
        font-size: 18px;
        font-weight: bold;
    }}

    QPushButton#clearBtn:hover {{
        color: {ACCENT};
    }}

    QPushButton#retryBtn {{
        background-color: {ACCENT};
        color: {SNOW};
        border: none;
        border-radius: 6px;
        padding: 10px 30px;
        font-family: {FONT_FAMILY};
        font-size: 14px;
        font-weight: bold;
    }}

    QPushButton#retryBtn:hover {{
        background-color: {ACCENT_HOVER};
    }}

    QProgressBar {{
        background-color: {SLATE_GREY};
        border: none;
        border-radius: 10px;
        height: 24px;
        text-align: center;
        color: {SNOW};
        font-size: 11px;
        font-weight: bold;
    }}

    QProgressBar::chunk {{
        background-color: {ACCENT};
        border-radius: 10px;
    }}

    QProgressBar#secondaryProgress {{
        height: 6px;
        border-radius: 3px;
    }}

    QProgressBar#secondaryProgress::chunk {{
        border-radius: 3px;
    }}
    """


def get_drop_zone_style():
    return f"""
        background-color: {GLUON_GREY};
        border: 2px dashed {ACCENT};
        border-radius: 8px;
        padding: 30px;
    """


def get_toggle_style(active=False):
    if active:
        return f"""
            background-color: {ACCENT};
            color: {SNOW};
            border: none;
            border-radius: 6px;
            padding: 8px 24px;
            font-family: {FONT_FAMILY};
            font-size: 13px;
            font-weight: bold;
        """
    return f"""
        background-color: {GLUON_GREY};
        color: {DUSTY_GREY};
        border: none;
        border-radius: 6px;
        padding: 8px 24px;
        font-family: {FONT_FAMILY};
        font-size: 13px;
    """


def get_mode_toggle_style(active=False, position="left"):
    if position == "left":
        tl = "20px"
        tr = "0px"
        br = "0px"
        bl = "20px"
    else:
        tl = "0px"
        tr = "20px"
        br = "20px"
        bl = "0px"

    if active:
        return f"""
            background-color: {ACCENT};
            color: {SNOW};
            border: none;
            border-top-left-radius: {tl};
            border-top-right-radius: {tr};
            border-bottom-right-radius: {br};
            border-bottom-left-radius: {bl};
            padding: 10px 28px;
            font-family: {FONT_FAMILY};
            font-size: 14px;
            font-weight: bold;
        """
    return f"""
        background-color: {GLUON_GREY};
        color: {DUSTY_GREY};
        border: none;
        border-top-left-radius: {tl};
        border-top-right-radius: {tr};
        border-bottom-right-radius: {br};
        border-bottom-left-radius: {bl};
        padding: 10px 28px;
        font-family: {FONT_FAMILY};
        font-size: 14px;
    """


def get_file_bar_style():
    return f"""
        background-color: {GLUON_GREY};
        border-radius: 8px;
    """


def get_warning_overlay_style():
    return f"""
        background-color: rgba(21, 20, 25, 200);
    """


def get_warning_card_style():
    return f"""
        background-color: {DARK_VOID};
        border: 2px solid {RED_DOT};
        border-radius: 12px;
        padding: 30px;
    """
