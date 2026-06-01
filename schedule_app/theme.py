import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

# 앱 전역 색·폰트·ttk 스타일.

COLORS = {
    "bg": "#f5f6fa",
    "card": "#ffffff",
    "header": "#eceff6",
    "primary": "#c8daf5",
    "primary_active": "#b3ccef",
    "primary_text": "#3d5a80",
    "danger": "#f5d0d0",
    "danger_active": "#ecc4c4",
    "danger_text": "#8b4a4a",
    "text": "#3d4555",
    "muted": "#7a8499",
    "border": "#dde2ec",
    "accent": "#b8e0f0",
    "toggle": "#e8e6f2",
    "toggle_active": "#dcd8ee",
}

PRIORITY_ROW_COLORS = {
    "urgent": "#fdeaea",
    "high": "#fff3e8",
    "normal": "#ffffff",
    "low": "#f4f6f9",
}

_font_family = None


def _resolve_font_family(root):
    global _font_family
    if _font_family is not None:
        return _font_family
    families = set(tkfont.families(root))
    for name in ("맑은 고딕", "Malgun Gothic", "Segoe UI", "Arial"):
        if name in families:
            _font_family = name
            return name
    _font_family = "TkDefaultFont"
    return _font_family


def font(root, size=10, bold=False):
    weight = "bold" if bold else "normal"
    return (_resolve_font_family(root), size, weight)


def apply_theme(root):
    _resolve_font_family(root)
    root.configure(bg=COLORS["bg"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"], font=font(root, 10))
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["card"])

    style.configure(
        "Title.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=font(root, 20, True),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["muted"],
        font=font(root, 10),
    )
    style.configure(
        "Status.TLabel",
        background=COLORS["header"],
        foreground=COLORS["muted"],
        font=font(root, 9),
        padding=(10, 6),
    )
    style.configure(
        "Hint.TLabel",
        background=COLORS["card"],
        foreground=COLORS["muted"],
        font=font(root, 9),
    )
    style.configure(
        "Empty.TLabel",
        background=COLORS["card"],
        foreground=COLORS["muted"],
        font=font(root, 11),
    )

    style.configure(
        "TLabelframe",
        background=COLORS["card"],
        bordercolor=COLORS["border"],
        relief="solid",
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["card"],
        foreground=COLORS["text"],
        font=font(root, 11, True),
    )

    style.configure("TLabel", background=COLORS["card"], foreground=COLORS["text"], font=font(root, 10))
    style.configure("TEntry", padding=4, fieldbackground=COLORS["card"])
    style.configure("TCombobox", padding=4)

    style.configure(
        "TButton",
        padding=(12, 7),
        font=font(root, 10),
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground=COLORS["primary_text"],
        font=font(root, 10, True),
        padding=(12, 7),
        bordercolor=COLORS["border"],
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["primary_active"]), ("pressed", COLORS["primary_active"])],
        foreground=[("disabled", COLORS["muted"])],
    )
    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground=COLORS["danger_text"],
        padding=(12, 7),
        bordercolor=COLORS["border"],
    )
    style.map(
        "Danger.TButton",
        background=[("active", COLORS["danger_active"]), ("pressed", COLORS["danger_active"])],
    )
    style.configure(
        "Toggle.TButton",
        background=COLORS["toggle"],
        foreground=COLORS["text"],
        font=font(root, 10),
        padding=(12, 7),
        bordercolor=COLORS["border"],
    )
    style.map(
        "Toggle.TButton",
        background=[("active", COLORS["toggle_active"]), ("pressed", COLORS["toggle_active"])],
    )

    style.configure(
        "Treeview",
        background=COLORS["card"],
        fieldbackground=COLORS["card"],
        foreground=COLORS["text"],
        rowheight=30,
        font=font(root, 10),
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["header"],
        foreground=COLORS["text"],
        font=font(root, 10, True),
        relief="flat",
        padding=(6, 8),
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["primary_active"])],
        foreground=[("selected", COLORS["primary_text"])],
    )


def style_toplevel(win, _root=None):
    win.configure(bg=COLORS["bg"])


def priority_tag(priority):
    return {"긴급": "urgent", "높음": "high", "보통": "normal", "낮음": "low"}.get(priority, "normal")
