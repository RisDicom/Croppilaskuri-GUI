"""Centralized Qt stylesheets for the application.

All CSS-like styling lives here instead of being embedded in widget code.
"""

from __future__ import annotations

from croppilaskuri.config.constants import COLOR_DEFAULT_BG


def get_global_stylesheet() -> str:
    """Return the application-wide Qt stylesheet."""
    return f"""
    /* ── Base ─────────────────────────────────────────────────── */
    QWidget {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 10pt;
    }}

    /* ── Framed input groups ──────────────────────────────────── */
    QFrame#InputGroup,
    QFrame#OptionsGroup,
    QFrame#OARGroup {{
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        margin: 0px;
        padding: 1px;
    }}

    /* ── Generic push-buttons ─────────────────────────────────── */
    QPushButton {{
        padding: 5px 10px;
        border-radius: 3px;
        border: 1px solid #b0b0b0;
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #f3f3f3, stop:1 #e2e2e2
        );
    }}
    QPushButton:hover {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f0f0f0
        );
        border: 1px solid #909090;
    }}
    QPushButton:pressed {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #e2e2e2, stop:1 #f3f3f3
        );
    }}

    /* ── Generate button (green) ──────────────────────────────── */
    QPushButton#GenerateButton {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #66bb6a, stop:1 #43a047
        );
        color: white;
        padding: 8px 15px;
        font-size: 11pt;
        font-weight: bold;
        border: 1px solid #388E3C;
    }}
    QPushButton#GenerateButton:hover {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #81c784, stop:1 #66bb6a
        );
        border: 1px solid #4caf50;
    }}
    QPushButton#GenerateButton:pressed {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #43a047, stop:1 #66bb6a
        );
    }}
    QPushButton#GenerateButton:disabled {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #e0e0e0, stop:1 #d0d0d0
        );
        color: #888888;
        border: 1px solid #b0b0b0;
    }}

    /* ── Small action buttons ─────────────────────────────────── */
    QPushButton#DeleteDoseButton,
    QPushButton.DeleteOARButton,
    QPushButton.ConfigureOARButton,
    QPushButton#FindNextButton,
    QPushButton#FindPrevButton,
    QPushButton#ClearSearchButton {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #f0f0f0, stop:1 #e0e0e0
        );
        border: 1px solid #c0c0c0;
        padding: 3px 6px;
        font-size: 9pt;
    }}
    QPushButton#DeleteDoseButton:hover,
    QPushButton.DeleteOARButton:hover,
    QPushButton.ConfigureOARButton:hover,
    QPushButton#FindNextButton:hover,
    QPushButton#FindPrevButton:hover,
    QPushButton#ClearSearchButton:hover {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f5f5f5
        );
        border: 1px solid #909090;
    }}
    QPushButton.DeleteOARButton {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #fddede, stop:1 #fcc2c2
        );
        border: 1px solid #fca4a4;
    }}
    QPushButton.DeleteOARButton:hover {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffecec, stop:1 #fddede
        );
        border: 1px solid #f88787;
    }}
    QPushButton#DeleteDoseButton:disabled {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #e0e0e0, stop:1 #d0d0d0
        );
        color: #888888;
        border: 1px solid #b0b0b0;
    }}
    QPushButton#FindNextButton:disabled,
    QPushButton#FindPrevButton:disabled {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #e0e0e0, stop:1 #d0d0d0
        );
        color: #aaaaaa;
        border: 1px solid #c0c0c0;
    }}

    /* ── Tab widget ───────────────────────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid #d0d0d0;
        border-top: none;
        margin-top: -1px;
        background-color: white;
    }}
    QTabBar::tab {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #f0f0f0, stop:1 #e0e0e0
        );
        border: 1px solid #c0c0c0;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 100px;
        padding: 7px 12px;
        margin-right: 1px;
        color: #333;
    }}
    QTabBar::tab:selected,
    QTabBar::tab:hover {{
        background: qlineargradient(
            x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f5f5f5
        );
    }}
    QTabBar::tab:selected {{
        border-color: #d0d0d0;
        margin-bottom: 0px;
        color: black;
        font-weight: bold;
    }}
    QTabBar::tab:!selected {{
        margin-top: 2px;
    }}

    /* ── Misc ─────────────────────────────────────────────────── */
    QScrollArea {{ border: none; }}
    #ScrollWidget {{ background-color: {COLOR_DEFAULT_BG}; }}
    QListWidget, QTableWidget {{ border: 1px solid #d0d0d0; }}
    QLineEdit {{ border: 1px solid #d0d0d0; padding: 3px; border-radius: 2px; }}
    QRadioButton {{ margin-top: 2px; margin-bottom: 2px; }}
    #SearchLineEdit {{ padding: 4px; }}
    """
