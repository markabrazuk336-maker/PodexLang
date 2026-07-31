"""Podex Studio — Visual Studio–style IDE for PodexLang."""

from __future__ import annotations

import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

STUDIO_DIR = Path(__file__).resolve().parent
if str(STUDIO_DIR) not in sys.path:
    sys.path.insert(0, str(STUDIO_DIR))

from build_service import BuildResult, Diagnostic, build_pdx, find_podexc, project_root, run_exe
from explorer import Explorer
from projects import TEMPLATES, create_project
from tabs import TabManager
from theme import COLORS, FONTS

APP_NAME = "Podex Studio"
ROOT = project_root()

NEW_FILE_TEMPLATE = """#profit <io>

fn main() -> int {
    print("Hello from Podex Studio!")
    return 0
}
"""


class PodexStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — PodexLang")
        self.geometry("1280x820")
        self.minsize(960, 580)
        self.configure(bg=COLORS["bg_panel"])

        self._busy = False
        self._diagnostics: list[Diagnostic] = []

        self._setup_style()
        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind_all("<Control-s>", lambda e: self.save_file())
        self.bind_all("<Control-S>", lambda e: self.save_file())
        self.bind_all("<Control-o>", lambda e: self.open_file_dialog())
        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-w>", lambda e: self.close_current_tab())
        self.bind_all("<F5>", lambda e: self.run_current())
        self.bind_all("<Control-b>", lambda e: self.build_current())
        self.bind_all("<F7>", lambda e: self.build_current())
        self.bind_all("<Control-Shift-N>", lambda e: self.new_project())

        self.explorer.load_project(ROOT)
        welcome = ROOT / "examples" / "math_demo.pdx"
        if welcome.is_file():
            self.open_path(welcome)
        else:
            self.tabs.new_untitled(NEW_FILE_TEMPLATE)

        self._update_title()
        self.after(200, self._check_toolchain)

    # ----- chrome -----

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=COLORS["bg_panel"], foreground=COLORS["fg"], font=FONTS["ui"])
        style.configure("TFrame", background=COLORS["bg_panel"])
        style.configure("TLabel", background=COLORS["bg_panel"], foreground=COLORS["fg"])
        style.configure(
            "TButton",
            background=COLORS["bg_input"],
            foreground=COLORS["fg"],
            borderwidth=0,
            padding=(10, 4),
            font=FONTS["ui"],
        )
        style.map(
            "TButton",
            background=[("active", COLORS["accent"]), ("pressed", COLORS["accent_hover"])],
            foreground=[("active", COLORS["fg_bright"])],
        )
        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground=COLORS["fg_bright"],
            padding=(12, 4),
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["accent_hover"]), ("pressed", COLORS["accent"])],
        )
        style.configure(
            "Treeview",
            background=COLORS["bg_sidebar"],
            foreground=COLORS["fg"],
            fieldbackground=COLORS["bg_sidebar"],
            borderwidth=0,
            rowheight=24,
            font=FONTS["ui"],
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["bg_select"])],
            foreground=[("selected", COLORS["fg_bright"])],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["bg_input"],
            troughcolor=COLORS["bg_panel"],
            borderwidth=0,
            arrowsize=12,
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=COLORS["bg_input"],
            troughcolor=COLORS["bg_panel"],
            borderwidth=0,
            arrowsize=12,
        )
        style.configure("TNotebook", background=COLORS["bg_panel"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=COLORS["bg_tab"],
            foreground=COLORS["fg_dim"],
            padding=(12, 4),
            font=FONTS["ui_small"],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["bg_tab_active"])],
            foreground=[("selected", COLORS["fg_bright"])],
        )

    def _build_menu(self) -> None:
        menubar = tk.Menu(
            self, tearoff=0, bg=COLORS["bg_toolbar"], fg=COLORS["fg"], activebackground=COLORS["accent"]
        )
        file_m = tk.Menu(
            menubar, tearoff=0, bg=COLORS["bg_toolbar"], fg=COLORS["fg"], activebackground=COLORS["accent"]
        )
        file_m.add_command(label="New File", accelerator="Ctrl+N", command=self.new_file)
        file_m.add_command(label="New Project...", accelerator="Ctrl+Shift+N", command=self.new_project)
        file_m.add_command(label="Open File...", accelerator="Ctrl+O", command=self.open_file_dialog)
        file_m.add_command(label="Open Folder...", command=self.open_folder)
        file_m.add_separator()
        file_m.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_m.add_command(label="Save As...", command=self.save_file_as)
        file_m.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_current_tab)
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_m)

        build_m = tk.Menu(
            menubar, tearoff=0, bg=COLORS["bg_toolbar"], fg=COLORS["fg"], activebackground=COLORS["accent"]
        )
        build_m.add_command(label="Build", accelerator="Ctrl+B / F7", command=self.build_current)
        build_m.add_command(label="Start Debugging (Run)", accelerator="F5", command=self.run_current)
        build_m.add_separator()
        build_m.add_command(label="Rebuild Compiler (podexc)", command=self.rebuild_compiler)
        menubar.add_cascade(label="Build", menu=build_m)

        help_m = tk.Menu(
            menubar, tearoff=0, bg=COLORS["bg_toolbar"], fg=COLORS["fg"], activebackground=COLORS["accent"]
        )
        help_m.add_command(label="About Podex Studio", command=self._about)
        menubar.add_cascade(label="Help", menu=help_m)
        self.config(menu=menubar)

    def _build_toolbar(self) -> None:
        bar = tk.Frame(self, bg=COLORS["bg_toolbar"], height=40)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        tk.Label(bar, text="  Podex", bg=COLORS["bg_toolbar"], fg=COLORS["fg_bright"], font=FONTS["title"]).pack(
            side="left", padx=(8, 0)
        )
        tk.Label(bar, text="Studio", bg=COLORS["bg_toolbar"], fg=COLORS["accent_hover"], font=FONTS["title"]).pack(
            side="left", padx=(4, 16)
        )

        def btn(text, cmd, accent=False):
            b = ttk.Button(bar, text=text, command=cmd, style="Accent.TButton" if accent else "TButton")
            b.pack(side="left", padx=3, pady=6)
            return b

        btn("New", self.new_file)
        btn("Project", self.new_project)
        btn("Open", self.open_file_dialog)
        btn("Save", self.save_file)
        tk.Frame(bar, bg=COLORS["border"], width=1).pack(side="left", fill="y", padx=8, pady=8)
        btn("Build", self.build_current)
        btn("▶ Run", self.run_current, accent=True)

        self.toolbar_file = tk.Label(
            bar, text="", bg=COLORS["bg_toolbar"], fg=COLORS["fg_dim"], font=FONTS["ui_small"], anchor="e"
        )
        self.toolbar_file.pack(side="right", padx=12)

    def _build_body(self) -> None:
        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned, width=240)
        self.explorer = Explorer(left, on_open_file=self.open_path)
        self.explorer.pack(fill="both", expand=True)
        paned.add(left, weight=0)

        right = ttk.Panedwindow(paned, orient="vertical")
        paned.add(right, weight=1)

        self.tabs = TabManager(right, on_active_changed=self._update_title)
        right.add(self.tabs, weight=3)

        bottom = ttk.Frame(right)
        self.bottom_nb = ttk.Notebook(bottom)
        self.bottom_nb.pack(fill="both", expand=True)

        # Output
        out_wrap = ttk.Frame(self.bottom_nb)
        out_header = tk.Frame(out_wrap, bg=COLORS["bg_panel"])
        out_header.pack(fill="x")
        ttk.Button(out_header, text="Clear", command=self._clear_output).pack(side="right", padx=6, pady=2)
        self.output = tk.Text(
            out_wrap,
            height=9,
            wrap="word",
            bg="#0c0c0c",
            fg=COLORS["fg"],
            insertbackground=COLORS["caret"],
            relief="flat",
            font=FONTS["mono_small"],
            padx=10,
            pady=8,
            state="disabled",
            cursor="arrow",
        )
        self.output.pack(fill="both", expand=True)
        self.output.tag_configure("err", foreground=COLORS["error"])
        self.output.tag_configure("ok", foreground=COLORS["success"])
        self.output.tag_configure("info", foreground=COLORS["accent_hover"])
        self.output.tag_configure("link", foreground="#4fc1ff", underline=True)
        self.output.tag_bind("link", "<Button-1>", self._on_output_link_click)
        self.output.tag_bind("link", "<Enter>", lambda e: self.output.configure(cursor="hand2"))
        self.output.tag_bind("link", "<Leave>", lambda e: self.output.configure(cursor="arrow"))
        self.bottom_nb.add(out_wrap, text="  Output  ")

        # Error List
        err_wrap = ttk.Frame(self.bottom_nb)
        cols = ("file", "line", "message")
        self.error_tree = ttk.Treeview(err_wrap, columns=cols, show="headings", selectmode="browse")
        self.error_tree.heading("file", text="File")
        self.error_tree.heading("line", text="Line")
        self.error_tree.heading("message", text="Description")
        self.error_tree.column("file", width=180, minwidth=80)
        self.error_tree.column("line", width=60, minwidth=40, anchor="center")
        self.error_tree.column("message", width=600, minwidth=200)
        self.error_tree.pack(fill="both", expand=True)
        self.error_tree.bind("<Double-1>", self._on_error_activate)
        self.error_tree.bind("<Return>", self._on_error_activate)
        self.bottom_nb.add(err_wrap, text="  Error List  ")

        right.add(bottom, weight=1)

    def _build_statusbar(self) -> None:
        bar = tk.Frame(self, bg=COLORS["bg_statusbar"], height=24)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self.status = tk.Label(
            bar, text="Ready", bg=COLORS["bg_statusbar"], fg=COLORS["fg_bright"], font=FONTS["ui_small"],
            anchor="w", padx=10,
        )
        self.status.pack(side="left", fill="y")
        self.status_right = tk.Label(
            bar, text="PodexLang → C++", bg=COLORS["bg_statusbar"], fg=COLORS["fg_bright"],
            font=FONTS["ui_small"], anchor="e", padx=10,
        )
        self.status_right.pack(side="right", fill="y")

    # ----- tabs / files -----

    def new_file(self) -> None:
        self.tabs.new_untitled(NEW_FILE_TEMPLATE)
        self._set_status("New file")

    def new_project(self) -> None:
        dlg = tk.Toplevel(self)
        dlg.title("New Project")
        dlg.configure(bg=COLORS["bg_panel"])
        dlg.transient(self)
        dlg.grab_set()
        dlg.geometry("420x260")
        dlg.resizable(False, False)

        tk.Label(dlg, text="Project name", bg=COLORS["bg_panel"], fg=COLORS["fg"], font=FONTS["ui"]).pack(
            anchor="w", padx=16, pady=(16, 4)
        )
        name_var = tk.StringVar(value="MyApp")
        name_entry = tk.Entry(
            dlg, textvariable=name_var, bg=COLORS["bg_input"], fg=COLORS["fg"],
            insertbackground=COLORS["caret"], relief="flat", font=FONTS["ui"],
        )
        name_entry.pack(fill="x", padx=16)
        name_entry.select_range(0, "end")
        name_entry.focus_set()

        tk.Label(dlg, text="Location", bg=COLORS["bg_panel"], fg=COLORS["fg"], font=FONTS["ui"]).pack(
            anchor="w", padx=16, pady=(12, 4)
        )
        loc_row = tk.Frame(dlg, bg=COLORS["bg_panel"])
        loc_row.pack(fill="x", padx=16)
        loc_var = tk.StringVar(value=str(ROOT / "projects"))
        loc_entry = tk.Entry(
            loc_row, textvariable=loc_var, bg=COLORS["bg_input"], fg=COLORS["fg"],
            insertbackground=COLORS["caret"], relief="flat", font=FONTS["ui"],
        )
        loc_entry.pack(side="left", fill="x", expand=True)

        def browse():
            p = filedialog.askdirectory(title="Project location", initialdir=loc_var.get())
            if p:
                loc_var.set(p)

        ttk.Button(loc_row, text="…", command=browse, width=3).pack(side="left", padx=(6, 0))

        tk.Label(dlg, text="Template", bg=COLORS["bg_panel"], fg=COLORS["fg"], font=FONTS["ui"]).pack(
            anchor="w", padx=16, pady=(12, 4)
        )
        tpl_var = tk.StringVar(value=next(iter(TEMPLATES)))
        tpl = ttk.Combobox(dlg, textvariable=tpl_var, values=list(TEMPLATES.keys()), state="readonly")
        tpl.pack(fill="x", padx=16)

        def create():
            name = name_var.get().strip()
            parent = Path(loc_var.get().strip())
            try:
                parent.mkdir(parents=True, exist_ok=True)
                main = create_project(parent, name, tpl_var.get())
            except Exception as e:
                messagebox.showerror(APP_NAME, str(e), parent=dlg)
                return
            dlg.destroy()
            self.explorer.load_project(main.parent)
            self.open_path(main)
            self._set_status(f"Created project {main.parent.name}")
            self._append_output(f"Created project: {main.parent}\n", "ok")

        btns = tk.Frame(dlg, bg=COLORS["bg_panel"])
        btns.pack(fill="x", padx=16, pady=16)
        ttk.Button(btns, text="Create", command=create, style="Accent.TButton").pack(side="right")
        ttk.Button(btns, text="Cancel", command=dlg.destroy).pack(side="right", padx=6)
        dlg.bind("<Return>", lambda e: create())

    def open_file_dialog(self) -> None:
        path = filedialog.askopenfilename(
            title="Open PodexLang file",
            initialdir=str(ROOT / "examples"),
            filetypes=[("PodexLang", "*.pdx"), ("All files", "*.*")],
        )
        if path:
            self.open_path(Path(path))

    def open_folder(self) -> None:
        path = filedialog.askdirectory(title="Open Folder", initialdir=str(ROOT))
        if path:
            self.explorer.load_project(Path(path))
            self._set_status(f"Opened folder: {path}")

    def open_path(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            messagebox.showerror(APP_NAME, f"Cannot open file:\n{e}")
            return
        self.tabs.open_path(path, text)
        self._set_status(f"Opened {path.name}")

    def save_file(self) -> bool:
        tab = self.tabs.current()
        if not tab:
            return False
        if tab.path is None:
            return self.save_file_as()
        try:
            tab.path.write_text(tab.editor.get_text(), encoding="utf-8")
            tab.editor.mark_saved()
            self.tabs.refresh_titles()
            self._update_title()
            self._set_status(f"Saved {tab.path.name}")
            return True
        except OSError as e:
            messagebox.showerror(APP_NAME, f"Cannot save:\n{e}")
            return False

    def save_file_as(self) -> bool:
        tab = self.tabs.current()
        if not tab:
            return False
        path = filedialog.asksaveasfilename(
            title="Save As",
            initialdir=str(ROOT / "examples"),
            defaultextension=".pdx",
            filetypes=[("PodexLang", "*.pdx"), ("All files", "*.*")],
        )
        if not path:
            return False
        tab.path = Path(path)
        return self.save_file()

    def close_current_tab(self) -> None:
        tab = self.tabs.current()
        if not tab:
            return
        if tab.editor.is_changed():
            r = messagebox.askyesnocancel(APP_NAME, f"Save changes to {self._tab_name(tab)}?")
            if r is None:
                return
            if r and not self.save_file():
                return
        self.tabs.close_tab(tab)
        if not self.tabs.tabs:
            self.tabs.new_untitled(NEW_FILE_TEMPLATE)

    def _tab_name(self, tab) -> str:
        return tab.path.name if tab.path else f"untitled{tab.untitled_id}.pdx"

    def _confirm_discard_all(self) -> bool:
        dirty = [t for t in self.tabs.tabs if t.editor.is_changed()]
        if not dirty:
            return True
        names = ", ".join(self._tab_name(t) for t in dirty[:5])
        r = messagebox.askyesnocancel(APP_NAME, f"Save changes to: {names}?")
        if r is None:
            return False
        if r:
            for t in dirty:
                self.tabs.select(t)
                if not self.save_file():
                    return False
        return True

    # ----- build / run -----

    def _ensure_saved_pdx(self) -> Path | None:
        tab = self.tabs.current()
        if not tab:
            return None
        if tab.editor.is_changed() or tab.path is None:
            if not self.save_file():
                return None
        assert tab.path is not None
        if tab.path.suffix != ".pdx":
            messagebox.showinfo(APP_NAME, "Build works with .pdx files.")
            return None
        return tab.path

    def build_current(self) -> None:
        if self._busy:
            return
        path = self._ensure_saved_pdx()
        if not path:
            return

        self._busy = True
        self._set_status("Building...")
        self._clear_errors()
        self._append_output(f"\n=== Build {path.name} ===\n", "info")

        def work():
            result = build_pdx(path, ROOT)
            self.after(0, lambda: self._on_build_done(result))

        threading.Thread(target=work, daemon=True).start()

    def _on_build_done(self, result: BuildResult) -> None:
        self._busy = False
        self._append_output(result.log, "ok" if result.ok else "err")
        self._show_diagnostics(result.diagnostics)
        self._set_status("Build succeeded" if result.ok else "Build failed")
        if not result.ok:
            if result.diagnostics:
                self.bottom_nb.select(1)
                self._jump_to_diagnostic(result.diagnostics[0])
            else:
                messagebox.showerror(APP_NAME, "Build failed — see Output.")

    def run_current(self) -> None:
        if self._busy:
            return
        path = self._ensure_saved_pdx()
        if not path:
            return

        self._busy = True
        self._set_status("Building & running...")
        self._clear_errors()

        def work():
            built = build_pdx(path, ROOT)

            def after_build():
                self._append_output(built.log, "ok" if built.ok else "err")
                self._show_diagnostics(built.diagnostics)
                if not built.ok or not built.exe_path:
                    self._busy = False
                    self._set_status("Build failed")
                    if built.diagnostics:
                        self.bottom_nb.select(1)
                        self._jump_to_diagnostic(built.diagnostics[0])
                    return

                def run_work():
                    ran = run_exe(built.exe_path)
                    self.after(0, lambda: self._on_run_done(ran))

                threading.Thread(target=run_work, daemon=True).start()

            self.after(0, after_build)

        threading.Thread(target=work, daemon=True).start()

    def _on_run_done(self, result: BuildResult) -> None:
        self._busy = False
        self._append_output(result.log, "ok" if result.ok else "err")
        self._set_status("Run finished" if result.ok else "Run failed")

    def rebuild_compiler(self) -> None:
        if self._busy:
            return
        self._busy = True
        self._set_status("Rebuilding podexc...")
        self._append_output("\n=== Rebuild podexc ===\n", "info")

        def work():
            from build_service import ensure_mingw_on_path
            import subprocess

            ensure_mingw_on_path()
            lines = []
            cmds = [
                [
                    "cmake", "-S", str(ROOT), "-B", str(ROOT / "build"), "-G", "MinGW Makefiles",
                    "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_CXX_COMPILER=g++",
                ],
                ["cmake", "--build", str(ROOT / "build"), "-j", "4"],
            ]
            ok = True
            for cmd in cmds:
                lines.append("> " + " ".join(cmd))
                r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
                lines.append(r.stdout)
                lines.append(r.stderr)
                if r.returncode != 0:
                    ok = False
                    break
            self.after(0, lambda: self._on_rebuild_done(ok, "\n".join(lines)))

        threading.Thread(target=work, daemon=True).start()

    def _on_rebuild_done(self, ok: bool, log: str) -> None:
        self._busy = False
        self._append_output(log, "ok" if ok else "err")
        self._set_status("Compiler rebuilt" if ok else "Compiler rebuild failed")
        self._check_toolchain()

    # ----- diagnostics -----

    def _clear_errors(self) -> None:
        self._diagnostics.clear()
        for i in self.error_tree.get_children():
            self.error_tree.delete(i)
        ed = self.tabs.current_editor()
        if ed:
            ed.clear_error_mark()

    def _show_diagnostics(self, diags: list[Diagnostic]) -> None:
        self._clear_errors()
        self._diagnostics = list(diags)
        for i, d in enumerate(diags):
            name = d.path.name if d.path else "?"
            iid = self.error_tree.insert(
                "", "end", iid=str(i), values=(name, f"{d.line}:{d.col}", d.message)
            )
            # also write clickable link in output
            loc = f"{d.path}:{d.line}:{d.col}" if d.path else f"line {d.line}:{d.col}"
            self._append_link(f"→ {loc}: {d.message}\n", i)

        if diags:
            self.status_right.configure(text=f"{len(diags)} error(s) — double-click to jump")

    def _append_link(self, text: str, diag_index: int) -> None:
        self.output.configure(state="normal")
        start = self.output.index("end-1c")
        self.output.insert("end", text, ("link", "err"))
        end = self.output.index("end-1c")
        tag = f"diag_{diag_index}"
        self.output.tag_add(tag, start, end)
        self.output.tag_bind(tag, "<Button-1>", lambda e, i=diag_index: self._jump_diag_index(i))
        self.output.see("end")
        self.output.configure(state="disabled")

    def _on_output_link_click(self, _event=None) -> None:
        pass  # per-diag tags handle clicks

    def _on_error_activate(self, _event=None) -> None:
        sel = self.error_tree.selection()
        if not sel:
            return
        try:
            idx = int(sel[0])
        except ValueError:
            return
        self._jump_diag_index(idx)

    def _jump_diag_index(self, idx: int) -> None:
        if 0 <= idx < len(self._diagnostics):
            self._jump_to_diagnostic(self._diagnostics[idx])

    def _jump_to_diagnostic(self, d: Diagnostic) -> None:
        if d.path and d.path.suffix == ".pdx" and d.path.is_file():
            self.open_path(d.path)
        ed = self.tabs.current_editor()
        if ed:
            ed.goto_line(d.line, d.col)
            self._set_status(f"Jumped to {d.path.name if d.path else 'file'}:{d.line}:{d.col}")

    # ----- ui helpers -----

    def _append_output(self, text: str, tag: str | None = None) -> None:
        self.output.configure(state="normal")
        if tag:
            self.output.insert("end", text, tag)
        else:
            self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _clear_output(self) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def _set_status(self, msg: str) -> None:
        self.status.configure(text=msg)

    def _update_title(self) -> None:
        tab = self.tabs.current()
        if not tab:
            self.title(APP_NAME)
            self.toolbar_file.configure(text="")
            return
        name = self._tab_name(tab)
        dirty = " *" if tab.editor.is_changed() else ""
        self.title(f"{name}{dirty} — {APP_NAME}")
        self.toolbar_file.configure(text=str(tab.path) if tab.path else "(unsaved)")
        self.tabs.refresh_titles()

    def _check_toolchain(self) -> None:
        podexc = find_podexc(ROOT)
        if podexc:
            self.status_right.configure(text=f"podexc ready · {podexc.name}")
        else:
            self.status_right.configure(text="podexc missing — Build → Rebuild Compiler")
            self._append_output(
                "Warning: podexc.exe not found. Use Build → Rebuild Compiler (podexc).\n",
                "err",
            )

    def _about(self) -> None:
        messagebox.showinfo(
            APP_NAME,
            "Podex Studio\n\n"
            "IDE for PodexLang — compile to C++ with #profit modules.\n\n"
            "Shortcuts:\n"
            "  Ctrl+N          New file\n"
            "  Ctrl+Shift+N    New project\n"
            "  Ctrl+W          Close tab\n"
            "  Ctrl+S          Save\n"
            "  Ctrl+B / F7     Build\n"
            "  F5              Run\n"
            "  Double-click Error List to jump\n",
        )

    def _on_close(self) -> None:
        if self._confirm_discard_all():
            self.destroy()


def main() -> None:
    app = PodexStudio()
    # Open files passed on the command line
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        if p.is_file():
            app.open_path(p)
    app.mainloop()


if __name__ == "__main__":
    main()
