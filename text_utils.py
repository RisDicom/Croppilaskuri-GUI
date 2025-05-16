# -*- coding: utf-8 -*-
"""
Tämä moduuli tarjoaa apufunktioita tekstin HTML-muotoiluun
käyttöliittymän RichText-elementtejä varten.
"""
from config import (
    COLOR_CODE, COLOR_VALUE, COLOR_PLACEHOLDER, COLOR_TOOL,
    COLOR_ACTION, COLOR_NOTE
)

def bold(text): return f'<b>{text}</b>'
def code(text): return f'<span style="font-weight:bold; color:{COLOR_CODE};">{text}</span>'
def value(text): return f'<span style="font-weight:bold; color:{COLOR_VALUE};">{str(text)}</span>'
def placeholder(text): return f'<i style="color:{COLOR_PLACEHOLDER};">{text}</i>'
def tool(text): return f'<i style="color:{COLOR_TOOL};">{text}</i>'
def action(text): return f'<b style="color:{COLOR_ACTION};">{text}</b>'
def note(text): return f'<i style="color:{COLOR_NOTE};">{text}</i>'