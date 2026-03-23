"""Application-wide constants: version, emoji, colors."""

from __future__ import annotations

# ── Version ─────────────────────────────────────────────────────────────
APP_VERSION: str = "v0.4.0"

# ── Emoji constants ─────────────────────────────────────────────────────
EMOJI_COPY: str = "\U0001f4cb"       # 📋
EMOJI_CROP_IN: str = "\u2702\ufe0f"  # ✂️
EMOJI_CROP_OUT: str = "\u2702\ufe0f"
EMOJI_UNION: str = "\u2795"          # ➕
EMOJI_RING: str = "\U0001f48d"       # 💍
EMOJI_MARGIN: str = "\u2194\ufe0f"   # ↔️
EMOJI_BOOLEAN: str = "\U0001f9e9"    # 🧩
EMOJI_CHECK: str = "\U0001f440"      # 👀
EMOJI_WARNING: str = "\u26a0\ufe0f"  # ⚠️
EMOJI_MANUAL: str = "\u270d\ufe0f"   # ✍️
EMOJI_INFO: str = "\u2139\ufe0f"     # ℹ️
EMOJI_DONE: str = "\u2705"           # ✅
EMOJI_SEARCH: str = "\U0001f50d"     # 🔍

# ── UI Colors ───────────────────────────────────────────────────────────
COLOR_COMPLETED_BG: str = "#e8f5e9"
COLOR_COMPLETED_FG: str = "#555555"
COLOR_DEFAULT_BG: str = "white"
COLOR_ALT_BG: str = "#f8f8f8"
COLOR_BORDER: str = "#d0d0d0"
COLOR_TITLE: str = "#003366"
COLOR_INSTRUCTION: str = "#333333"
COLOR_CODE: str = "#000080"
COLOR_VALUE: str = "#005000"
COLOR_PLACEHOLDER: str = "#444444"
COLOR_TOOL: str = "#005000"
COLOR_ACTION: str = "#c00000"
COLOR_NOTE: str = "#555555"
COLOR_SEARCH_HIGHLIGHT_BG: str = "#fff3cd"
COLOR_SEARCH_HIGHLIGHT_BORDER: str = "#ffc107"

# ── Fixed domain values ─────────────────────────────────────────────────
DEFAULT_RING_PREFIX: str = "NT"
DEFAULT_DPTV_OAR_CROP_CM: float = 0.1
V_PREFIX: str = "v"
CROP_SUFFIX: str = "crop"
