"""Code editor with line numbers and PodexLang syntax highlighting."""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk

from theme import COLORS, FONTS


KEYWORDS = {
    "fn", "let", "mut", "if", "else", "while", "for", "in",
    "return", "break", "continue",
    "true", "false", "and", "or", "not",
}
TYPES = {"int", "float", "bool", "string", "void"}


class CodeEditor(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.path: str | None = None
        self._changed = False
        self._highlight_job = None

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.linenumbers = tk.Canvas(
            self,
            width=52,
            bg=COLORS["line_num_bg"],
            highlightthickness=0,
            bd=0,
        )
        self.linenumbers.grid(row=0, column=0, sticky="ns")

        self.text = tk.Text(
            self,
            wrap="none",
            undo=True,
            maxundo=-1,
            bg=COLORS["bg"],
            fg=COLORS["fg"],
            insertbackground=COLORS["caret"],
            selectbackground=COLORS["bg_select"],
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=8,
            font=FONTS["mono"],
            tabs=("4c",),
        )
        self.text.grid(row=0, column=1, sticky="nsew")

        ys = ttk.Scrollbar(self, orient="vertical", command=self._on_scroll)
        ys.grid(row=0, column=2, sticky="ns")
        xs = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        xs.grid(row=1, column=1, sticky="ew")

        self.text.configure(yscrollcommand=lambda *a: self._yscroll(ys, *a), xscrollcommand=xs.set)

        self._configure_tags()
        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", self._schedule_highlight)
        self.text.bind("<Button-1>", lambda e: self.after(1, self._redraw_linenumbers))
        self.text.bind("<MouseWheel>", lambda e: self.after(1, self._redraw_linenumbers))
        self.text.bind("<Configure>", lambda e: self._redraw_linenumbers())

        self._redraw_linenumbers()

    def _configure_tags(self) -> None:
        self.text.tag_configure("kw", foreground=COLORS["syn_kw"])
        self.text.tag_configure("type", foreground=COLORS["syn_type"])
        self.text.tag_configure("string", foreground=COLORS["syn_string"])
        self.text.tag_configure("number", foreground=COLORS["syn_number"])
        self.text.tag_configure("comment", foreground=COLORS["syn_comment"])
        self.text.tag_configure("profit", foreground=COLORS["syn_profit"])
        self.text.tag_configure("fnname", foreground=COLORS["syn_fn"])
        self.text.tag_configure("error_line", background="#4b1818")

    def _on_scroll(self, *args):
        self.text.yview(*args)
        self._redraw_linenumbers()

    def _yscroll(self, scrollbar, *args):
        scrollbar.set(*args)
        self._redraw_linenumbers()

    def _redraw_linenumbers(self) -> None:
        self.linenumbers.delete("all")
        i = self.text.index("@0,0")
        while True:
            dline = self.text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.linenumbers.create_text(
                46,
                y,
                anchor="ne",
                text=linenum,
                fill=COLORS["line_num"],
                font=FONTS["mono_small"],
            )
            i = self.text.index(f"{i}+1line")

    def _on_modified(self, _event=None):
        if self.text.edit_modified():
            self._changed = True
            self.event_generate("<<EditorChanged>>")
            self.text.edit_modified(False)
            self._redraw_linenumbers()

    def _schedule_highlight(self, _event=None):
        if self._highlight_job is not None:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(80, self.highlight)

    def set_text(self, content: str, path: str | None = None) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.path = path
        self._changed = False
        self.text.edit_modified(False)
        self.highlight()
        self._redraw_linenumbers()

    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def is_changed(self) -> bool:
        return self._changed

    def mark_saved(self) -> None:
        self._changed = False
        self.text.edit_modified(False)

    def focus_editor(self) -> None:
        self.text.focus_set()

    def goto_line(self, line: int, col: int = 1) -> None:
        line = max(1, line)
        col = max(0, col - 1)
        index = f"{line}.{col}"
        self.text.mark_set("insert", index)
        self.text.see(index)
        self.text.tag_remove("sel", "1.0", "end")
        self.text.tag_add("sel", f"{line}.0", f"{line}.0 lineend")
        self.clear_error_mark()
        self.text.tag_add("error_line", f"{line}.0", f"{line}.0 lineend")
        self.focus_editor()

    def clear_error_mark(self) -> None:
        self.text.tag_remove("error_line", "1.0", "end")

    def highlight(self) -> None:
        content = self.get_text()
        for tag in ("kw", "type", "string", "number", "comment", "profit", "fnname"):
            self.text.tag_remove(tag, "1.0", "end")

        # line comments // and #
        for m in re.finditer(r"(//.*)|(^#[^\n]*profit[^\n]*)|(^#[^\n]*)", content, re.M):
            start, end = m.span()
            chunk = content[start:end]
            tag = "profit" if "#profit" in chunk else "comment"
            self._tag_span(start, end, tag)

        # strings
        for m in re.finditer(r'"(?:\\.|[^"\\])*"', content):
            self._tag_span(*m.span(), "string")

        # numbers
        for m in re.finditer(r"\b\d+(?:\.\d+)?\b", content):
            self._tag_span(*m.span(), "number")

        # keywords / types / fn names
        for m in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b", content):
            word = m.group(0)
            if word in KEYWORDS:
                self._tag_span(*m.span(), "kw")
            elif word in TYPES:
                self._tag_span(*m.span(), "type")

        for m in re.finditer(r"\bfn\s+([A-Za-z_][A-Za-z0-9_]*)", content):
            self._tag_span(m.start(1), m.end(1), "fnname")

        self._highlight_job = None
        self._redraw_linenumbers()

    def _tag_span(self, start: int, end: int, tag: str) -> None:
        s = self._index_from_offset(start)
        e = self._index_from_offset(end)
        self.text.tag_add(tag, s, e)

    def _index_from_offset(self, offset: int) -> str:
        # Convert absolute char offset to tk Text index
        return f"1.0+{offset}c"
