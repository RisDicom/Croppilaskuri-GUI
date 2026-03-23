"""Text formatting utilities for HTML output.

Provides small helper functions used by guide_logic and
optimization_criteria to build styled HTML fragments.
"""

from __future__ import annotations


def bold(text: str) -> str:
    """Wrap *text* in an HTML ``<b>`` tag."""
    return f"<b>{text}</b>"


def html_escape(text: str) -> str:
    """Escape basic HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def code_span(text: str) -> str:
    """Wrap *text* in a styled HTML ``<code>`` tag."""
    return (
        f'<code style="background:#f0f0f0;padding:1px 4px;'
        f'border-radius:2px;font-family:monospace;">{html_escape(text)}</code>'
    )


# ── Aliases used by guide_logic & optimization_criteria ─────────


def code(text: str) -> str:
    """Alias for :func:`code_span` — used by legacy modules."""
    return code_span(text)


def value(text: str) -> str:
    """Wrap *text* in a ``<span class='value'>`` tag."""
    return f"<span class='value'>{text}</span>"


def note(text: str) -> str:
    """Wrap *text* in an italic ``<span class='note'>`` tag."""
    return f"<span class='note'>{text}</span>"


def tool(text: str) -> str:
    """Wrap *text* as an Eclipse tool name (green, bold)."""
    return f"<span style='color:#005000;font-weight:bold;'>{text}</span>"


def action(text: str) -> str:
    """Wrap *text* as a user action (red, bold)."""
    return f"<span style='color:#c00000;font-weight:bold;'>{text}</span>"
