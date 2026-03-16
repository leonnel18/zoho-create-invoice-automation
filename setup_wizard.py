"""
setup_wizard.py
Zoho Create Invoice Automation — Setup Wizard
Title: "Zoho Create Invoice Automation by leonnel18"

Cross-platform (Windows + Mac) guided setup wizard.
Collects .env values, installs dependencies, and configures the daily scheduler.
"""

import os
import sys
import json
import platform
import subprocess
import threading
import webbrowser
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from functools import partial

# ── Version & Repo ────────────────────────────────────────────────────────────

VERSION     = "1.0.0"
GITHUB_REPO = "leonnel18/zoho-create-invoice-automation"
GITHUB_API  = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_URL  = f"https://github.com/{GITHUB_REPO}/releases/latest"

# ── Donation Details ──────────────────────────────────────────────────────────

GCASH = {
    "Mobile Number": "09625408076",
    "Name":          "Gideon Noel Valera",
}
BANK = {
    "Name":           "Gideon Noel Sarmiento Valera",
    "Account Number": "2005141027",
    "Bank Code":      "01828-001-6",
    "Bank Name":      "Wise Pilipinas Inc.",
}

# ── Theme detection ───────────────────────────────────────────────────────────

def _detect_dark_mode() -> bool:
    """Detect OS dark mode. Returns True if dark, False if light."""
    if platform.system() == "Windows":
        try:
            import winreg  # type: ignore[import]
            key = winreg.OpenKey(  # type: ignore[attr-defined]
                winreg.HKEY_CURRENT_USER,  # type: ignore[attr-defined]
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")  # type: ignore[attr-defined]
            winreg.CloseKey(key)  # type: ignore[attr-defined]
            return val == 0
        except Exception:
            return False
    elif platform.system() == "Darwin":
        try:
            out = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True,
            )
            return out.stdout.strip().lower() == "dark"
        except Exception:
            return False
    return False


# ── Firefox Design System palette ─────────────────────────────────────────────
# Colors sourced from Mozilla Photon Design System + mozilla.design/firefox

_LIGHT_THEME = dict(
    header_bg   = "#20123a",   # Ink 90  — deep Firefox navy-purple
    header_fg   = "#ffffff",
    header_sub  = "#c2a7ff",   # violet tint for subtitle
    bg          = "#f9f9fb",   # Grey 10
    card_bg     = "#ffffff",
    text        = "#0c0c0d",   # Grey 90
    muted       = "#737373",   # Grey 50
    accent      = "#0060df",   # Blue 60
    green       = "#058b00",   # Green 60
    border      = "#d7d7db",   # Grey 30
    info_bg     = "#deeafc",
    info_bd     = "#80bdff",
    info_txt    = "#0060df",
    success_bg  = "#d5f7e7",
    success_bd  = "#3fe1b0",   # Green 40
    success_txt = "#058b00",
    tip_bg      = "#fff8e5",
    tip_bd      = "#ffca2c",
    tip_txt     = "#7a5200",
    review_hdr  = "#f1f5f9",
)

_DARK_THEME = dict(
    header_bg   = "#15141a",   # darkest Firefox dark
    header_fg   = "#fbfbfe",
    header_sub  = "#c2a7ff",
    bg          = "#1c1b22",   # Firefox dark background
    card_bg     = "#2b2a33",   # slightly elevated surface
    text        = "#fbfbfe",
    muted       = "#cfcfd8",
    accent      = "#0a84ff",   # Blue 50  — vivid on dark
    green       = "#3fe1b0",   # Green 40 — neon on dark
    border      = "#52525e",
    info_bg     = "#1e3251",
    info_bd     = "#0060df",
    info_txt    = "#80bdff",
    success_bg  = "#0c2821",
    success_bd  = "#3fe1b0",
    success_txt = "#3fe1b0",
    tip_bg      = "#2a1f00",
    tip_bd      = "#7a5200",
    tip_txt     = "#ffd700",
    review_hdr  = "#232231",
)

_DARK_MODE = _detect_dark_mode()
_T = _DARK_THEME if _DARK_MODE else _LIGHT_THEME

# ── Constants ─────────────────────────────────────────────────────────────────

APP_TITLE   = "Zoho Create Invoice Automation by leonnel18"
WIN_WIDTH   = 680
WIN_HEIGHT  = 680

# Theme-resolved colors
HEADER_BG   = _T["header_bg"]
HEADER_FG   = _T["header_fg"]
HEADER_SUB  = _T["header_sub"]
ACCENT      = _T["accent"]
GREEN       = _T["green"]
BG          = _T["bg"]
CARD_BG     = _T["card_bg"]
TEXT        = _T["text"]
MUTED       = _T["muted"]
BORDER      = _T["border"]
INFO_BG     = _T["info_bg"]
INFO_BORDER = _T["info_bd"]
INFO_TEXT   = _T["info_txt"]
SUCCESS_BG  = _T["success_bg"]
SUCCESS_BDR = _T["success_bd"]
SUCCESS_TXT = _T["success_txt"]
TIP_BG      = _T["tip_bg"]
TIP_BORDER  = _T["tip_bd"]
TIP_TEXT    = _T["tip_txt"]
REVIEW_HDR  = _T["review_hdr"]
BTN_SEC     = "#3a3944" if _DARK_MODE else "#e2e8f0"   # secondary button bg

# ── Fonts ──────────────────────────────────────────────────────────────────────
# Metropolis (headlines) + Inter (body) — Firefox Design System type stack.
# Falls back gracefully to system sans-serif if neither is installed.

FONT_TITLE  = "Metropolis"   # display / headings
FONT_BODY   = "Inter"        # labels, fields, body copy

BASE_DIR    = Path(__file__).parent
ENV_PATH    = BASE_DIR / ".env"
SCRIPT_PATH = BASE_DIR / "tools" / "orchestrator.py"
REQ_PATH    = BASE_DIR / "requirements.txt"

STEPS = ["Welcome", "Zoho Credentials", "Folder Settings", "Schedule", "Review & Install"]

HOURS = [
    ("00", "12:00 AM — Midnight"), ("01", "1:00 AM"),  ("02", "2:00 AM"),
    ("03", "3:00 AM"),  ("04", "4:00 AM"),  ("05", "5:00 AM"),
    ("06", "6:00 AM"),  ("07", "7:00 AM"),  ("08", "8:00 AM — Morning"),
    ("09", "9:00 AM"),  ("10", "10:00 AM"), ("11", "11:00 AM"),
    ("12", "12:00 PM — Noon"), ("13", "1:00 PM"), ("14", "2:00 PM"),
    ("15", "3:00 PM"),  ("16", "4:00 PM"),  ("17", "5:00 PM"),
    ("18", "6:00 PM — Evening"), ("19", "7:00 PM"), ("20", "8:00 PM"),
    ("21", "9:00 PM"),  ("22", "10:00 PM"), ("23", "11:00 PM"),
]
HOUR_DISPLAY = [f"{h} — {label}" for h, label in HOURS]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _version_tuple(v: str) -> tuple:
    """Convert '1.2.3' → (1, 2, 3) for comparison."""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except ValueError:
        return (0, 0, 0)


def _center(win: tk.Toplevel, w: int, h: int):
    """Center a Toplevel window on screen."""
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


import math as _math


def _darken(hex_color: str, factor: float = 0.82) -> str:
    """Return a darker shade of a hex color."""
    rgb = bytes.fromhex(hex_color.lstrip("#"))
    return "#{:02x}{:02x}{:02x}".format(
        int(rgb[0] * factor), int(rgb[1] * factor), int(rgb[2] * factor)
    )


def _card(parent, **kwargs) -> tk.Frame:
    return tk.Frame(parent, bg=CARD_BG, relief=tk.FLAT,
                    highlightbackground=BORDER, highlightthickness=1, **kwargs)


def _label(parent, text, size=10, bold=False, color=TEXT, **kwargs) -> tk.Label:
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text, font=(FONT_BODY, size, weight),
                    bg=parent["bg"], fg=color, **kwargs)


def _btn(parent, text, command, color=ACCENT, fg="#ffffff", width=None) -> tk.Button:
    """Flat button with hover colour shift — UIverse rude-wolverine-24 style."""
    kw: dict = {"width": width} if width else {}
    hover = _darken(color)
    btn = tk.Button(parent, text=text, font=(FONT_BODY, 10, "bold"),
                    bg=color, fg=fg,
                    activebackground=hover, activeforeground=fg,
                    relief=tk.FLAT, bd=0, padx=20, pady=8,
                    cursor="hand2", command=command, **kw)
    btn.bind("<Enter>", lambda *_: btn.config(bg=hover))
    btn.bind("<Leave>", lambda *_: btn.config(bg=color))
    return btn


class _FieldEntry(tk.Frame):
    """Entry with animated bottom-border on focus — UIverse good-donkey-28 style."""

    def __init__(self, parent, textvariable: tk.StringVar,
                 show: str = "", **kwargs):
        bg = parent["bg"] if isinstance(parent, tk.Frame) else CARD_BG
        super().__init__(parent, bg=bg)

        self._entry = tk.Entry(
            self, textvariable=textvariable, show=show,
            font=(FONT_BODY, 10), relief=tk.FLAT, bd=0,
            bg=CARD_BG, fg=TEXT,
            insertbackground=TEXT,
            highlightthickness=0,
            **kwargs,
        )
        self._entry.pack(fill=tk.X, ipady=6)

        # Bottom accent bar
        self._bar = tk.Frame(self, bg=BORDER, height=2)
        self._bar.pack(fill=tk.X)

        self._entry.bind("<FocusIn>",  lambda *_: self._bar.config(bg=ACCENT))
        self._entry.bind("<FocusOut>", lambda *_: self._bar.config(bg=BORDER))

    def pack(self, **kw):  # type: ignore[override]
        super().pack(**kw)
        return self

    def grid(self, **kw):  # type: ignore[override]
        super().grid(**kw)
        return self


class _DotLoader(tk.Canvas):
    """Three-dot bouncing loader — UIverse bright-lizard-8 inspired."""

    _COLORS = ["#952bb9", "#c044d8", "#ff4f5e"]   # purple → pink Firefox palette

    def __init__(self, parent, dot_r: int = 7, gap: int = 18):
        self._r   = dot_r
        self._gap = gap
        w = (dot_r * 2 + gap) * 3 + gap
        h = dot_r * 2 + 20
        super().__init__(parent, width=w, height=h, bg=BG, highlightthickness=0)
        self._lw = w   # avoid overwriting tkinter's internal self._w
        self._lh = h
        self._phase = 0
        self._job: str | None = None

    def start(self) -> None:
        self._animate()

    def stop(self) -> None:
        if job := self._job:
            self.after_cancel(job)
            self._job = None
        self.delete("all")

    def _animate(self) -> None:
        self.delete("all")
        r, gap = self._r, self._gap
        cx_base = gap + r
        cy = self._lh // 2
        for i, color in enumerate(self._COLORS):
            offset = int(_math.sin(self._phase * 0.18 + i * 1.1) * (r + 4))
            cx = cx_base + i * (r * 2 + gap)
            self.create_oval(cx - r, cy - r + offset,
                             cx + r, cy + r + offset,
                             fill=color, outline="")
        self._phase += 1
        self._job = self.after(45, lambda *_: self._animate())


# ── Icon helpers ──────────────────────────────────────────────────────────────
# PNG icons loaded from assets/icons/*.png (drop any 24×24 PNGs there).
# Falls back to text glyphs if the file isn't present.

ASSETS_DIR = BASE_DIR / "assets" / "icons"

_icon_cache: dict[str, tk.PhotoImage] = {}

def _icon(name: str) -> tk.PhotoImage | None:
    """Return a PhotoImage for *name* or None if the asset isn't available."""
    if name in _icon_cache:
        return _icon_cache[name]
    path = ASSETS_DIR / f"{name}.png"
    if path.exists():
        try:
            img = tk.PhotoImage(file=str(path))
            _icon_cache[name] = img
            return img
        except Exception:
            pass
    return None


# Glyph fallbacks used when PNG icons aren't present
_GLYPHS = {
    "welcome":     "◈",
    "credentials": "⚙",
    "folders":     "⊡",
    "schedule":    "◷",
    "review":      "◉",
    "success":     "✦",
    "tips":        "◆",
    "info":        "◇",
    "check":       "✔",
    "skip":        "›",
}


# ── Wizard ────────────────────────────────────────────────────────────────────

class SetupWizard:
    def __init__(self):
        # Fix blurry/clipped UI on Windows HiDPI displays
        if platform.system() == "Windows":
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]
            except Exception:
                pass

        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.resizable(True, True)
        self.root.minsize(620, 600)
        self.root.configure(bg=BG)

        # Center window on screen
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - WIN_WIDTH)  // 2
        y  = max(0, (sh - WIN_HEIGHT) // 2)
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}+{x}+{y}")

        # Widget attributes — declared here, assigned in _build_ui() / _page_*()
        self.step_row:    tk.Frame
        self.content:     tk.Frame
        self.pages:       list[tk.Frame]
        self.btn_back:    tk.Button
        self.btn_next:    tk.Button
        self.sched_sub:   tk.Frame
        self.hour_combo:  ttk.Combobox
        self.review_card: tk.Frame

        # Schedule boolean — kept separate so self.v stays Dict[str, StringVar]
        self.schedule_enabled = tk.BooleanVar(value=True)

        # Form variables (all StringVar)
        self.v: dict[str, tk.StringVar] = {
            "client_id":     tk.StringVar(),
            "client_secret": tk.StringVar(),
            "refresh_token": tk.StringVar(),
            "org_id":        tk.StringVar(),
            "input_folder":  tk.StringVar(),
            "output_folder": tk.StringVar(),
            "db_path":       tk.StringVar(),
            "schedule_hour": tk.StringVar(value=HOUR_DISPLAY[18]),  # default 6 PM
        }

        self._load_existing_env()
        self.current_step = 0
        self._build_ui()
        self._show_page(0)
        self._check_for_updates()

    # ── Pre-fill from existing .env ───────────────────────────────────────────

    def _load_existing_env(self):
        if not ENV_PATH.exists():
            return
        mapping = {
            "ZOHO_CLIENT_ID":     "client_id",
            "ZOHO_CLIENT_SECRET": "client_secret",
            "ZOHO_REFRESH_TOKEN": "refresh_token",
            "ZOHO_ORG_ID":        "org_id",
            "INPUT_FOLDER":       "input_folder",
            "OUTPUT_FOLDER":      "output_folder",
            "DB_PATH":            "db_path",
        }
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            if key.strip() in mapping:
                self.v[mapping[key.strip()]].set(val.strip())

    # ── UI Shell ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header
        header = tk.Frame(self.root, bg=HEADER_BG, height=86)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Zoho Create Invoice Automation",
                 font=(FONT_TITLE, 17, "bold"), bg=HEADER_BG, fg=HEADER_FG,
                 ).place(relx=0.5, rely=0.36, anchor="center")
        tk.Label(header, text="by leonnel18",
                 font=(FONT_BODY, 9), bg=HEADER_BG, fg=HEADER_SUB,
                 ).place(relx=0.5, rely=0.70, anchor="center")

        # Version label (top-left)
        tk.Label(header, text=f"v{VERSION}",
                 font=(FONT_BODY, 8), bg=HEADER_BG, fg=HEADER_SUB,
                 ).place(relx=0.02, rely=0.72, anchor="w")

        # Buy me a Matcha button (top-right)
        matcha_btn = tk.Button(
            header, text="🍵  Buy me a Matcha",
            font=(FONT_BODY, 9, "bold"),
            bg="#15803d", fg="#ffffff",
            relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2", bd=0,
            activebackground="#166534", activeforeground="#ffffff",
            command=self._show_donation,
        )
        matcha_btn.place(relx=0.98, rely=0.5, anchor="e")

        # ── Step indicator
        self.step_row = tk.Frame(self.root, bg=BG, pady=7)
        self.step_row.pack(fill=tk.X, padx=30)
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X, padx=20)

        # ── Content
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill=tk.BOTH, expand=True, padx=30, pady=(14, 0))

        # ── Build pages
        self.pages = [
            self._page_welcome(),
            self._page_credentials(),
            self._page_folders(),
            self._page_schedule(),
            self._page_review(),
        ]

        # ── Footer
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X, padx=20, pady=(6, 0))
        footer = tk.Frame(self.root, bg=BG, pady=10)
        footer.pack(fill=tk.X, padx=30)

        self.btn_back = _btn(footer, "← Back", self._go_back,
                             color=BTN_SEC, fg=TEXT)
        self.btn_back.pack(side=tk.LEFT)

        self.btn_next = _btn(footer, "Next →", self._go_next, color=ACCENT)
        self.btn_next.pack(side=tk.RIGHT)

    def _build_step_indicator(self):
        for w in self.step_row.winfo_children():
            w.destroy()
        for i in range(len(STEPS)):
            done   = i < self.current_step
            active = i == self.current_step
            # Pill dot
            dot_bg = GREEN if done else (ACCENT if active else BORDER)
            dot    = tk.Frame(self.step_row, bg=dot_bg, width=10, height=10)
            dot.pack(side=tk.LEFT, padx=(0, 2))
            dot.pack_propagate(False)
            if active:
                tk.Label(self.step_row, text=STEPS[i],
                         font=(FONT_BODY, 8, "bold"), bg=BG, fg=ACCENT,
                         ).pack(side=tk.LEFT, padx=(0, 6))
            if i < len(STEPS) - 1:
                tk.Frame(self.step_row, bg=BORDER, width=20, height=1
                         ).pack(side=tk.LEFT, padx=2)

    # ── Pages ─────────────────────────────────────────────────────────────────

    def _page_welcome(self) -> tk.Frame:
        f = tk.Frame(self.content, bg=BG)
        row0 = tk.Frame(f, bg=BG)
        row0.pack(anchor="w", pady=(0, 8))
        _label(row0, _GLYPHS["welcome"] + "  ", size=17, bold=True, color=ACCENT).pack(side=tk.LEFT)
        _label(row0, "Welcome!", size=17, bold=True).pack(side=tk.LEFT)

        card = _card(f)
        card.pack(fill=tk.BOTH, expand=True)

        body = tk.Frame(card, bg=CARD_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=18, pady=14)

        _label(body, "What does this app do?", bold=True, size=11).pack(anchor="w", pady=(0, 6))

        features = [
            (_GLYPHS["check"], "Reads delivery receipt PDFs from a folder you choose"),
            (_GLYPHS["check"], "Automatically creates invoices in your Zoho Books account"),
            (_GLYPHS["check"], "Saves the generated invoice PDFs to an output folder"),
            (_GLYPHS["check"], "Marks processed receipts as done (renames the file)"),
            (_GLYPHS["check"], "Runs automatically every day at a time you set"),
        ]
        for icon, text in features:
            row = tk.Frame(body, bg=CARD_BG)
            row.pack(anchor="w", pady=2)
            tk.Label(row, text=icon, font=(FONT_BODY, 10, "bold"),
                     bg=CARD_BG, fg=ACCENT).pack(side=tk.LEFT)
            _label(row, f"  {text}", color=MUTED).pack(side=tk.LEFT)

        tk.Frame(body, bg=BORDER, height=1).pack(fill=tk.X, pady=10)

        _label(body, "Before you begin, please have ready:", bold=True, size=10).pack(anchor="w", pady=(0, 4))
        prereqs = [
            "Your Zoho Books API credentials  (Client ID, Client Secret, Refresh Token, Org ID)",
            "The folder path where your delivery receipt PDFs are stored",
            "A folder path where you want the generated invoices to be saved",
        ]
        for item in prereqs:
            _label(body, f"  •  {item}", color=MUTED, size=9).pack(anchor="w", pady=1)

        return f

    def _page_credentials(self) -> tk.Frame:
        f = tk.Frame(self.content, bg=BG)
        row0 = tk.Frame(f, bg=BG)
        row0.pack(anchor="w", pady=(0, 2))
        _label(row0, _GLYPHS["credentials"] + "  ", size=15, bold=True, color=ACCENT).pack(side=tk.LEFT)
        _label(row0, "Zoho API Credentials", size=15, bold=True).pack(side=tk.LEFT)
        _label(f, "These allow the app to connect to your Zoho Books account securely.",
               color=MUTED).pack(anchor="w", pady=(0, 8))

        info = tk.Frame(f, bg=INFO_BG, highlightbackground=INFO_BORDER, highlightthickness=1)
        info.pack(fill=tk.X, pady=(0, 8))
        _label(info, f"{_GLYPHS['info']}  Get these from:  api-console.zoho.com  →  Self Client",
               color=INFO_TEXT, size=9).pack(padx=12, pady=6, anchor="w")

        fields = [
            ("Client ID",       "client_id",      "Identifies your app in Zoho",             False),
            ("Client Secret",   "client_secret",  "Your app's private key — keep this safe", True),
            ("Refresh Token",   "refresh_token",  "Long-lived token for API access",          True),
            ("Organization ID", "org_id",          "Your Zoho Books company ID",              False),
        ]

        card = _card(f)
        card.pack(fill=tk.BOTH, expand=True)
        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        for label, key, hint, is_pw in fields:
            row = tk.Frame(inner, bg=CARD_BG)
            row.pack(fill=tk.X, pady=6)

            tk.Label(row, text=label, font=(FONT_BODY, 9, "bold"),
                     bg=CARD_BG, fg=MUTED, width=17, anchor="w").pack(side=tk.LEFT)

            col = tk.Frame(row, bg=CARD_BG)
            col.pack(side=tk.LEFT, fill=tk.X, expand=True)

            _FieldEntry(col, textvariable=self.v[key],
                        show="●" if is_pw else "").pack(fill=tk.X)
            _label(col, f"  {hint}", color=MUTED, size=8).pack(anchor="w", pady=(1, 0))

        return f

    def _page_folders(self) -> tk.Frame:
        f = tk.Frame(self.content, bg=BG)
        row0 = tk.Frame(f, bg=BG)
        row0.pack(anchor="w", pady=(0, 2))
        _label(row0, _GLYPHS["folders"] + "  ", size=15, bold=True, color=ACCENT).pack(side=tk.LEFT)
        _label(row0, "Folder Settings", size=15, bold=True).pack(side=tk.LEFT)
        _label(f, "Tell the app where to find receipts and where to save generated invoices.",
               color=MUTED).pack(anchor="w", pady=(0, 8))

        folders = [
            ("Input Folder",   "input_folder",  False,
             "The folder where your delivery receipt PDFs are stored."),
            ("Output Folder",  "output_folder", False,
             "The folder where generated invoice PDFs will be saved."),
            ("Database File",  "db_path",        True,
             "Tracking database — e.g. C:\\data\\invoices.db"),
        ]

        for title, key, is_file, hint in folders:
            grp = tk.LabelFrame(f, text=f"  {title}  ",
                                font=(FONT_BODY, 9, "bold"), bg=BG, fg=TEXT,
                                relief=tk.FLAT, highlightbackground=BORDER,
                                highlightthickness=1, padx=10, pady=8)
            grp.pack(fill=tk.X, pady=5)

            row = tk.Frame(grp, bg=BG)
            row.pack(fill=tk.X)

            _FieldEntry(row, textvariable=self.v[key]).pack(
                side=tk.LEFT, fill=tk.X, expand=True)

            def _make_browse(k: str, file_mode: bool):
                def _cmd():
                    self._browse_file(k) if file_mode else self._browse_folder(k)
                return _cmd
            cmd = _make_browse(key, is_file)
            tk.Button(row, text="Browse...", font=(FONT_BODY, 9),
                      bg=BTN_SEC, fg=TEXT, relief=tk.FLAT, padx=10, pady=5,
                      cursor="hand2", command=cmd).pack(side=tk.LEFT, padx=(6, 0))

            _label(grp, hint, color=MUTED, size=8).pack(anchor="w", pady=(3, 0))

        return f

    def _page_schedule(self) -> tk.Frame:
        f = tk.Frame(self.content, bg=BG)
        row0 = tk.Frame(f, bg=BG)
        row0.pack(anchor="w", pady=(0, 2))
        _label(row0, _GLYPHS["schedule"] + "  ", size=15, bold=True, color=ACCENT).pack(side=tk.LEFT)
        _label(row0, "Automatic Schedule", size=15, bold=True).pack(side=tk.LEFT)
        _label(f, "Choose when the app should run automatically every day.",
               color=MUTED).pack(anchor="w", pady=(0, 8))

        card = _card(f)
        card.pack(fill=tk.X, pady=(0, 10))
        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(fill=tk.X, padx=16, pady=14)

        tk.Checkbutton(inner, text="  Enable automatic daily run",
                       variable=self.schedule_enabled,
                       font=(FONT_BODY, 11, "bold"), bg=CARD_BG, fg=TEXT,
                       activebackground=CARD_BG, cursor="hand2",
                       command=self._toggle_schedule).pack(anchor="w")

        self.sched_sub = tk.Frame(inner, bg=CARD_BG)
        self.sched_sub.pack(fill=tk.X, padx=24, pady=(8, 0))

        _label(self.sched_sub, "Run every day at:", size=10).pack(side=tk.LEFT)

        self.hour_combo = ttk.Combobox(self.sched_sub,
                                       textvariable=self.v["schedule_hour"],
                                       values=HOUR_DISPLAY,
                                       width=28, font=(FONT_BODY, 10),
                                       state="readonly")
        self.hour_combo.pack(side=tk.LEFT, padx=10)

        # Tips card
        tips_card = tk.Frame(f, bg=TIP_BG, highlightbackground=TIP_BORDER, highlightthickness=1)
        tips_card.pack(fill=tk.X, pady=4)
        tips = tk.Frame(tips_card, bg=TIP_BG)
        tips.pack(fill=tk.X, padx=14, pady=10)
        _label(tips, "💡  Tips", bold=True, color=TIP_TEXT, size=10).pack(anchor="w")
        _label(tips, "• You can run the pipeline manually anytime by double-clicking  run_pipeline.bat",
               color=TIP_TEXT, size=9).pack(anchor="w", pady=2)
        _label(tips, "• The app is smart — it won't process the same receipt twice.",
               color=TIP_TEXT, size=9).pack(anchor="w", pady=2)
        _label(tips, "• Receipts are renamed after processing so you always know what's done.",
               color=TIP_TEXT, size=9).pack(anchor="w", pady=2)

        return f

    def _page_review(self) -> tk.Frame:
        f = tk.Frame(self.content, bg=BG)
        row0 = tk.Frame(f, bg=BG)
        row0.pack(anchor="w", pady=(0, 2))
        _label(row0, _GLYPHS["review"] + "  ", size=15, bold=True, color=ACCENT).pack(side=tk.LEFT)
        _label(row0, "Review & Install", size=15, bold=True).pack(side=tk.LEFT)
        _label(f, "Check your settings below, then click Install Now to finish.",
               color=MUTED).pack(anchor="w", pady=(0, 8))

        self.review_card = _card(f)
        self.review_card.pack(fill=tk.BOTH, expand=True)
        return f

    def _populate_review(self):
        for w in self.review_card.winfo_children():
            w.destroy()

        hour_val     = self.v["schedule_hour"].get()
        schedule_str = f"Daily at {hour_val}" if self.schedule_enabled.get() else "Disabled (manual only)"

        sections = [
            ("🔑  Zoho Credentials", [
                ("Client ID",      self.v["client_id"].get()      or "— not set —"),
                ("Organization ID", self.v["org_id"].get()         or "— not set —"),
                ("Client Secret",  "●●●●●●●● (hidden)"            if self.v["client_secret"].get() else "— not set —"),
                ("Refresh Token",  "●●●●●●●● (hidden)"            if self.v["refresh_token"].get() else "— not set —"),
            ]),
            ("📁  Folder Settings", [
                ("Input Folder",  self.v["input_folder"].get()  or "— not set —"),
                ("Output Folder", self.v["output_folder"].get() or "— not set —"),
                ("Database File", self.v["db_path"].get()       or "— not set —"),
            ]),
            ("⏰  Schedule", [
                ("Auto-run", schedule_str),
            ]),
        ]

        for sec_title, rows in sections:
            hdr = tk.Frame(self.review_card, bg=REVIEW_HDR)
            hdr.pack(fill=tk.X)
            _label(hdr, f"  {sec_title}", bold=True, size=9, color=MUTED).pack(
                side=tk.LEFT, padx=8, pady=5)

            for lbl, val in rows:
                is_missing = val == "— not set —"
                row = tk.Frame(self.review_card, bg=CARD_BG)
                row.pack(fill=tk.X)
                tk.Label(row, text=f"    {lbl}", font=(FONT_BODY, 9),
                         bg=CARD_BG, fg=MUTED, width=20, anchor="w").pack(side=tk.LEFT, pady=3)
                tk.Label(row, text=val, font=(FONT_BODY, 9, "bold" if not is_missing else "normal"),
                         bg=CARD_BG, fg="#dc2626" if is_missing else TEXT, anchor="w",
                         wraplength=380).pack(side=tk.LEFT, padx=4, pady=3)

    # ── Navigation ────────────────────────────────────────────────────────────

    def _show_page(self, index: int):
        for p in self.pages:
            p.pack_forget()
        self.current_step = index
        self._build_step_indicator()

        if index == len(STEPS) - 1:
            self._populate_review()
            self.btn_next.config(text="  ✅  Install Now  ", bg=GREEN)
        else:
            self.btn_next.config(text="Next →", bg=ACCENT)

        self.btn_back.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
        self.pages[index].pack(fill=tk.BOTH, expand=True)

    def _go_next(self):
        if not self._validate():
            return
        if self.current_step == len(STEPS) - 1:
            self._install()
        else:
            self._show_page(self.current_step + 1)

    def _go_back(self):
        if self.current_step > 0:
            self._show_page(self.current_step - 1)

    def _validate(self) -> bool:
        step = self.current_step
        if step == 1:
            missing = [label for label, key, _, _ in [
                ("Client ID",       "client_id",      "", False),
                ("Client Secret",   "client_secret",  "", False),
                ("Refresh Token",   "refresh_token",  "", False),
                ("Organization ID", "org_id",         "", False),
            ] if not self.v[key].get().strip()]
            if missing:
                messagebox.showwarning("Missing Fields",
                    f"Please fill in the following fields:\n\n" + "\n".join(f"  • {m}" for m in missing))
                return False
        elif step == 2:
            for label, key in [("Input Folder", "input_folder"),
                                ("Output Folder", "output_folder"),
                                ("Database File", "db_path")]:
                if not self.v[key].get().strip():
                    messagebox.showwarning("Missing Field", f"Please set the {label}.")
                    return False
        return True

    def _toggle_schedule(self):
        state = tk.NORMAL if self.schedule_enabled.get() else tk.DISABLED
        for w in self.sched_sub.winfo_children():
            cfg = getattr(w, "config", None)
            if callable(cfg):
                try:
                    cfg(state=state)
                except tk.TclError:
                    pass

    # ── Browse dialogs ────────────────────────────────────────────────────────

    def _browse_folder(self, key: str):
        path = filedialog.askdirectory(title="Select Folder")
        if path:
            sep = "\\" if platform.system() == "Windows" else "/"
            self.v[key].set(path.replace("/", sep))

    def _browse_file(self, key: str):
        path = filedialog.asksaveasfilename(
            title="Choose Database File Location",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            initialfile="invoices.db",
        )
        if path:
            sep = "\\" if platform.system() == "Windows" else "/"
            self.v[key].set(path.replace("/", sep))

    # ── Install ───────────────────────────────────────────────────────────────

    def _install(self):
        self.btn_next.config(state=tk.DISABLED, text="  Installing…")
        self.btn_back.config(state=tk.DISABLED)

        # Overlay animated loader
        loader_frame = tk.Frame(self.content, bg=BG)
        loader_frame.place(relx=0.5, rely=0.5, anchor="center")
        _label(loader_frame, "Installing, please wait…", color=MUTED, size=10
               ).pack(pady=(0, 12))
        loader = _DotLoader(loader_frame)
        loader.pack()
        loader.start()
        self.root.update()

        def _do_install() -> None:
            steps: list[str] = []
            error: Exception | None = None
            try:
                self._write_env()
                steps.append(f"{_GLYPHS['check']}  Configuration saved to .env")
                self._install_requirements()
                steps.append(f"{_GLYPHS['check']}  Python dependencies installed")
                if self.schedule_enabled.get():
                    self._setup_scheduler()
                    steps.append(f"{_GLYPHS['check']}  Scheduler set — daily at {self.v['schedule_hour'].get()}")
                else:
                    steps.append(f"{_GLYPHS['skip']}  Scheduler skipped (manual mode)")
            except Exception as exc:
                error = exc
            self.root.after(0, lambda *_: _finish(steps, error))

        def _finish(steps: list[str], error: Exception | None) -> None:
            loader.stop()
            loader_frame.destroy()
            if error:
                messagebox.showerror(
                    "Installation Failed",
                    f"Something went wrong:\n\n{error}\n\nPlease check your settings and try again."
                )
                self.btn_next.config(state=tk.NORMAL, text="  Install Now  ", bg=GREEN)
                self.btn_back.config(state=tk.NORMAL)
            else:
                self._show_success(steps)

        threading.Thread(target=_do_install, daemon=True).start()

    def _write_env(self):
        hour = self.v["schedule_hour"].get().split(" ")[0]  # extract "18" from "18 — 6:00 PM"
        content = (
            "# Zoho Create Invoice Automation — Environment Config\n"
            "# Generated by Setup Wizard\n\n"
            "# --- Folder Paths ---\n"
            f"INPUT_FOLDER={self.v['input_folder'].get()}\n"
            f"OUTPUT_FOLDER={self.v['output_folder'].get()}\n\n"
            "# --- Database ---\n"
            f"DB_PATH={self.v['db_path'].get()}\n\n"
            "# --- Zoho Books REST API ---\n"
            f"ZOHO_CLIENT_ID={self.v['client_id'].get()}\n"
            f"ZOHO_CLIENT_SECRET={self.v['client_secret'].get()}\n"
            f"ZOHO_REFRESH_TOKEN={self.v['refresh_token'].get()}\n"
            f"ZOHO_ORG_ID={self.v['org_id'].get()}\n"
            "ZOHO_REGION=com\n\n"
            "# --- Invoice Defaults ---\n"
            "DEFAULT_ITEM_RATE=1.00\n"
            "DEFAULT_CUSTOMER_NAME=Generic\n"
        )
        ENV_PATH.write_text(content, encoding="utf-8")

    def _install_requirements(self):
        if REQ_PATH.exists():
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(REQ_PATH), "-q"],
                check=True
            )

    def _setup_scheduler(self):
        hour_raw = self.v["schedule_hour"].get().split(" ")[0].zfill(2)
        python   = sys.executable
        script   = str(SCRIPT_PATH)

        if platform.system() == "Windows":
            subprocess.run([
                "schtasks", "/create",
                "/tn", "ZohoCreateInvoiceAutomation",
                "/tr", f'"{python}" "{script}"',
                "/sc", "daily",
                "/st", f"{hour_raw}:00",
                "/f",
            ], check=True, capture_output=True)

        else:  # macOS
            label     = "com.leonnel18.zoho-invoice-automation"
            plist_dir = Path.home() / "Library" / "LaunchAgents"
            plist_dir.mkdir(parents=True, exist_ok=True)
            plist     = plist_dir / f"{label}.plist"
            log_dir   = BASE_DIR / ".tmp"
            log_dir.mkdir(exist_ok=True)

            plist.write_text(
                f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                f'"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                f'<plist version="1.0"><dict>\n'
                f'  <key>Label</key><string>{label}</string>\n'
                f'  <key>ProgramArguments</key><array>\n'
                f'    <string>{python}</string>\n'
                f'    <string>{script}</string>\n'
                f'  </array>\n'
                f'  <key>StartCalendarInterval</key><dict>\n'
                f'    <key>Hour</key><integer>{int(hour_raw)}</integer>\n'
                f'    <key>Minute</key><integer>0</integer>\n'
                f'  </dict>\n'
                f'  <key>StandardOutPath</key><string>{log_dir}/launchd.log</string>\n'
                f'  <key>StandardErrorPath</key><string>{log_dir}/launchd_error.log</string>\n'
                f'</dict></plist>\n'
            )
            subprocess.run(["launchctl", "load", str(plist)], check=True)

    # ── Success screen ────────────────────────────────────────────────────────

    def _show_success(self, steps_done: list):
        for p in self.pages:
            p.pack_forget()

        done_frame = tk.Frame(self.content, bg=BG)
        done_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(done_frame, text=_GLYPHS["success"],
                 font=(FONT_TITLE, 44, "bold"), bg=BG, fg=GREEN).pack(pady=(10, 4))
        _label(done_frame, "Setup Complete!", size=20, bold=True, color=GREEN).pack()
        _label(done_frame, "The app is ready to use.", color=MUTED, size=10).pack(pady=(2, 10))

        card = tk.Frame(done_frame, bg=SUCCESS_BG, highlightbackground=SUCCESS_BDR, highlightthickness=1)
        card.pack(fill=tk.X)
        inner = tk.Frame(card, bg=SUCCESS_BG)
        inner.pack(fill=tk.X, padx=16, pady=12)

        for line in steps_done:
            _label(inner, line, color=SUCCESS_TXT, size=10).pack(anchor="w", pady=2)

        tk.Frame(inner, bg=SUCCESS_BDR, height=1).pack(fill=tk.X, pady=8)

        _label(inner, "To run the pipeline manually at any time:", bold=True,
               color=SUCCESS_TXT, size=10).pack(anchor="w")
        _label(inner, "  →  Double-click  run_pipeline.bat  in the project folder",
               color=SUCCESS_TXT, size=10).pack(anchor="w", pady=(2, 0))

        self.btn_next.config(state=tk.NORMAL, text="  Close  ",
                             bg="#475569", command=self.root.destroy)
        self.btn_back.config(state=tk.DISABLED)

    # ── Update Check ─────────────────────────────────────────────────────────

    def _check_for_updates(self):
        """Run in background thread — silently skips if no internet or no releases."""
        def _fetch():
            try:
                req  = urllib.request.Request(GITHUB_API,
                       headers={"User-Agent": "zoho-invoice-wizard"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data    = json.loads(resp.read().decode())
                    latest  = data.get("tag_name", "").lstrip("v")
                    if not latest:
                        return
                    if _version_tuple(latest) > _version_tuple(VERSION):
                        self.root.after(0, lambda *_: self._show_update_dialog(latest))
            except Exception:
                pass  # no internet / no releases yet — silent

        threading.Thread(target=_fetch, daemon=True).start()

    def _show_update_dialog(self, latest: str):
        win = tk.Toplevel(self.root)
        win.title("Update Available")
        win.geometry("420x220")
        win.resizable(False, False)
        win.configure(bg=BG)
        win.grab_set()
        _center(win, 420, 220)

        tk.Label(win, text="🆕  Update Available!",
                 font=(FONT_BODY, 14, "bold"), bg=BG, fg=ACCENT).pack(pady=(22, 4))
        tk.Label(win, text=f"A new version is available:  v{latest}",
                 font=(FONT_BODY, 10), bg=BG, fg=TEXT).pack()
        tk.Label(win, text=f"You currently have:  v{VERSION}",
                 font=(FONT_BODY, 10), bg=BG, fg=MUTED).pack(pady=(2, 16))

        row = tk.Frame(win, bg=BG)
        row.pack()
        _btn(row, "Download Update",
             lambda: (webbrowser.open(GITHUB_URL), win.destroy()),
             color=ACCENT).pack(side=tk.LEFT, padx=8)
        tk.Button(row, text="Skip for Now",
                  font=(FONT_BODY, 10), bg=BTN_SEC, fg=TEXT,
                  relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
                  command=win.destroy).pack(side=tk.LEFT)

    # ── Donation Modal ────────────────────────────────────────────────────────

    def _show_donation(self):
        win = tk.Toplevel(self.root)
        win.title("Buy me a Matcha 🍵")
        win.geometry("400x340")
        win.resizable(False, False)
        win.configure(bg=BG)
        win.grab_set()
        _center(win, 400, 340)

        # Header
        hdr = tk.Frame(win, bg="#15803d", height=64)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🍵  Buy me a Matcha",
                 font=(FONT_BODY, 14, "bold"), bg="#15803d", fg="#ffffff",
                 ).place(relx=0.5, rely=0.42, anchor="center")
        tk.Label(hdr, text="This app is free — a small gift keeps it growing!",
                 font=(FONT_BODY, 8), bg="#15803d", fg="#bbf7d0",
                 ).place(relx=0.5, rely=0.78, anchor="center")

        # Tab switcher
        donation_tab = tk.StringVar(value="gcash")
        tab_row = tk.Frame(win, bg="#f0fdf4")
        tab_row.pack(fill=tk.X)

        def _switch(tab: str) -> None:
            donation_tab.set(tab)
            for k, btn in tab_btns.items():
                btn.config(bg="#15803d" if k == tab else "#dcfce7",
                           fg="#ffffff"  if k == tab else "#166534")
            for k, frm in tab_frames.items():
                frm.pack_forget() if k != tab else frm.pack(fill=tk.BOTH, expand=True, padx=24, pady=14)

        def _make_switch(k: str):
            def _cmd():
                _switch(k)
            return _cmd

        tab_btns = {}
        for key, label in [("gcash", "📱  GCash"), ("bank", "🏦  Bank Transfer")]:
            b = tk.Button(tab_row, text=label,
                          font=(FONT_BODY, 10, "bold"),
                          bg="#15803d" if key == "gcash" else "#dcfce7",
                          fg="#ffffff"  if key == "gcash" else "#166534",
                          relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
                          command=_make_switch(key))
            b.pack(side=tk.LEFT, expand=True, fill=tk.X)
            tab_btns[key] = b

        tk.Frame(win, bg=BORDER, height=1).pack(fill=tk.X)

        # Tab content frames
        tab_frames = {}

        # GCash tab
        gcash_frm = tk.Frame(win, bg=BG)
        for label, value in GCASH.items():
            self._donation_row(gcash_frm, label, value)
        tab_frames["gcash"] = gcash_frm

        # Bank Transfer tab
        bank_frm = tk.Frame(win, bg=BG)
        for label, value in BANK.items():
            self._donation_row(bank_frm, label, value)
        tab_frames["bank"] = bank_frm

        # Show GCash by default
        gcash_frm.pack(fill=tk.BOTH, expand=True, padx=24, pady=14)

        # Thank you note
        tk.Label(win, text="Thank you for your support! 💚",
                 font=(FONT_BODY, 9, "italic"), bg=BG, fg="#15803d").pack(pady=(0, 10))

    def _donation_row(self, parent: tk.Frame, label: str, value: str):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill=tk.X, pady=5)

        tk.Label(row, text=label, font=(FONT_BODY, 9, "bold"),
                 bg=BG, fg=MUTED, width=18, anchor="w").pack(side=tk.LEFT)

        val_var = tk.StringVar(value=value)
        entry = tk.Entry(row, textvariable=val_var, font=(FONT_BODY, 10, "bold"),
                         fg=TEXT, bg=CARD_BG, relief=tk.FLAT,
                         highlightbackground=BORDER, highlightthickness=1,
                         state="readonly", readonlybackground=CARD_BG)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        def _copy(v=value):
            self.root.clipboard_clear()
            self.root.clipboard_append(v)
            copy_btn.config(text="✔ Copied!")
            self.root.after(1500, lambda *_: copy_btn.config(text="Copy"))

        copy_btn = tk.Button(row, text="Copy",
                             font=(FONT_BODY, 8), bg=BTN_SEC, fg=TEXT,
                             relief=tk.FLAT, padx=8, pady=4, cursor="hand2",
                             command=_copy)
        copy_btn.pack(side=tk.LEFT, padx=(6, 0))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    SetupWizard().run()
