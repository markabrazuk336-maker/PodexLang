"""Multi-document tab bar for Podex Studio."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import ttk
from typing import Callable

from editor import CodeEditor
from theme import COLORS, FONTS


@dataclass
class Tab:
    frame: ttk.Frame
    editor: CodeEditor
    path: Path | None = None
    button: tk.Frame = field(default=None)  # type: ignore
    title_label: tk.Label = field(default=None)  # type: ignore
    close_btn: tk.Label = field(default=None)  # type: ignore
    untitled_id: int = 0


class TabManager(ttk.Frame):
    def __init__(
        self,
        master,
        on_active_changed: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.on_active_changed = on_active_changed
        self.tabs: list[Tab] = []
        self.active: Tab | None = None
        self._untitled_seq = 0

        self.tabbar = tk.Frame(self, bg=COLORS["bg_tab"], height=32)
        self.tabbar.pack(fill="x")
        self.tabbar.pack_propagate(False)

        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)
        self.body.rowconfigure(0, weight=1)
        self.body.columnconfigure(0, weight=1)

    def current(self) -> Tab | None:
        return self.active

    def current_editor(self) -> CodeEditor | None:
        return self.active.editor if self.active else None

    def current_path(self) -> Path | None:
        return self.active.path if self.active else None

    def open_path(self, path: Path, content: str) -> Tab:
        path = path.resolve()
        for t in self.tabs:
            if t.path and t.path.resolve() == path:
                self.select(t)
                return t
        return self._add_tab(content=content, path=path)

    def new_untitled(self, content: str) -> Tab:
        self._untitled_seq += 1
        return self._add_tab(content=content, path=None, untitled_id=self._untitled_seq)

    def _add_tab(self, content: str, path: Path | None, untitled_id: int = 0) -> Tab:
        frame = ttk.Frame(self.body)
        editor = CodeEditor(frame)
        editor.pack(fill="both", expand=True)
        editor.set_text(content, str(path) if path else None)
        editor.bind("<<EditorChanged>>", lambda e: self._on_editor_changed())

        tab = Tab(frame=frame, editor=editor, path=path, untitled_id=untitled_id)
        self._make_tab_button(tab)
        self.tabs.append(tab)
        self.select(tab)
        return tab

    def _make_tab_button(self, tab: Tab) -> None:
        btn = tk.Frame(self.tabbar, bg=COLORS["bg_tab"], cursor="hand2")
        btn.pack(side="left", fill="y", padx=(0, 1))

        title = tk.Label(
            btn,
            text=self._title_for(tab),
            bg=COLORS["bg_tab"],
            fg=COLORS["fg"],
            font=FONTS["ui"],
            padx=10,
            pady=6,
        )
        title.pack(side="left")

        close = tk.Label(
            btn,
            text="×",
            bg=COLORS["bg_tab"],
            fg=COLORS["fg_dim"],
            font=FONTS["ui"],
            padx=6,
            cursor="hand2",
        )
        close.pack(side="right")

        tab.button = btn
        tab.title_label = title
        tab.close_btn = close

        for w in (btn, title):
            w.bind("<Button-1>", lambda e, t=tab: self.select(t))
        close.bind("<Button-1>", lambda e, t=tab: self.close_tab(t))
        close.bind("<Enter>", lambda e: close.configure(fg=COLORS["error"]))
        close.bind("<Leave>", lambda e: close.configure(fg=COLORS["fg_dim"]))

    def _title_for(self, tab: Tab) -> str:
        dirty = " *" if tab.editor.is_changed() else ""
        if tab.path:
            return f"{tab.path.name}{dirty}"
        n = tab.untitled_id or 1
        return f"untitled{n}.pdx{dirty}"

    def select(self, tab: Tab) -> None:
        if self.active is tab:
            self._refresh_tab_styles()
            if self.on_active_changed:
                self.on_active_changed()
            return

        if self.active:
            self.active.frame.grid_remove()

        self.active = tab
        tab.frame.grid(row=0, column=0, sticky="nsew")
        self._refresh_tab_styles()
        tab.editor.focus_editor()
        if self.on_active_changed:
            self.on_active_changed()

    def _refresh_tab_styles(self) -> None:
        for t in self.tabs:
            active = t is self.active
            bg = COLORS["bg_tab_active"] if active else COLORS["bg_tab"]
            fg = COLORS["fg_bright"] if active else COLORS["fg_dim"]
            t.button.configure(bg=bg)
            t.title_label.configure(bg=bg, fg=fg, text=self._title_for(t))
            t.close_btn.configure(bg=bg)

    def _on_editor_changed(self) -> None:
        self._refresh_tab_styles()
        if self.on_active_changed:
            self.on_active_changed()

    def close_tab(self, tab: Tab | None = None) -> bool:
        """Return False if user cancelled (caller should confirm save first)."""
        tab = tab or self.active
        if not tab:
            return True

        idx = self.tabs.index(tab)
        tab.button.destroy()
        tab.frame.destroy()
        self.tabs.remove(tab)

        if self.active is tab:
            self.active = None
            if self.tabs:
                self.select(self.tabs[min(idx, len(self.tabs) - 1)])
            elif self.on_active_changed:
                self.on_active_changed()
        return True

    def refresh_titles(self) -> None:
        self._refresh_tab_styles()

    def find_by_path(self, path: Path) -> Tab | None:
        path = path.resolve()
        for t in self.tabs:
            if t.path and t.path.resolve() == path:
                return t
        return None

    def any_dirty(self) -> bool:
        return any(t.editor.is_changed() for t in self.tabs)
