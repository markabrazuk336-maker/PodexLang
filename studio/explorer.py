"""Solution Explorer – project file tree."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from theme import COLORS, FONTS


class Explorer(ttk.Frame):
    def __init__(self, master, on_open_file, **kwargs):
        super().__init__(master, **kwargs)
        self.on_open_file = on_open_file
        self.root_path: Path | None = None

        header = tk.Frame(self, bg=COLORS["bg_sidebar"], height=28)
        header.pack(fill="x")
        tk.Label(
            header,
            text="SOLUTION EXPLORER",
            bg=COLORS["bg_sidebar"],
            fg=COLORS["fg_dim"],
            font=FONTS["ui_small"],
            padx=10,
            pady=6,
            anchor="w",
        ).pack(fill="x")

        self.tree = ttk.Treeview(self, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<Double-1>", self._on_double)
        self.tree.bind("<Return>", self._on_double)

        self._paths: dict[str, Path] = {}

    def load_project(self, root: Path) -> None:
        self.root_path = root
        self.tree.delete(*self.tree.get_children())
        self._paths.clear()

        root_id = self.tree.insert("", "end", text=f"  {root.name}", open=True)
        self._paths[root_id] = root

        # Prefer showing useful folders first
        preferred = ["examples", "stdlib", "studio", "compiler"]
        shown = set()
        for name in preferred:
            p = root / name
            if p.is_dir():
                self._insert_dir(root_id, p)
                shown.add(name)

        for p in sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if p.name.startswith(".") or p.name in ("build", "out") or p.name in shown:
                continue
            if p.is_dir():
                self._insert_dir(root_id, p)
            elif p.suffix in {".pdx", ".md", ".bat", ".txt"} or p.name == "CMakeLists.txt":
                self._insert_file(root_id, p)

    def _insert_dir(self, parent: str, path: Path) -> str:
        node = self.tree.insert(parent, "end", text=f"  {path.name}", open=False)
        self._paths[node] = path
        # dummy child so expand arrow shows
        dummy = self.tree.insert(node, "end", text="...")
        self._paths[dummy] = path / ".dummy"
        return node

    def _insert_file(self, parent: str, path: Path) -> str:
        icon = "◆" if path.suffix == ".pdx" else "○"
        node = self.tree.insert(parent, "end", text=f"  {icon} {path.name}")
        self._paths[node] = path
        return node

    def _on_open(self, _event=None):
        item = self.tree.focus()
        if not item:
            return
        path = self._paths.get(item)
        if not path or not path.is_dir():
            return
        # clear dummy children and populate
        for child in self.tree.get_children(item):
            self.tree.delete(child)
        try:
            entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        except OSError:
            return
        for p in entries:
            if p.name.startswith(".") or p.name == "build":
                continue
            if p.is_dir():
                self._insert_dir(item, p)
            elif p.suffix in {".pdx", ".md", ".bat", ".txt", ".py", ".hpp", ".cpp"} or p.name == "CMakeLists.txt":
                self._insert_file(item, p)

    def _on_double(self, _event=None):
        item = self.tree.focus()
        if not item:
            return
        path = self._paths.get(item)
        if path and path.is_file():
            self.on_open_file(path)
