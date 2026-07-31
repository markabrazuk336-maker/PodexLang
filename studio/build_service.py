"""Build & run PodexLang sources via podexc + g++."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Diagnostic:
    path: Path | None
    line: int
    col: int
    message: str
    raw: str


@dataclass
class BuildResult:
    ok: bool
    log: str
    exe_path: Path | None = None
    cpp_path: Path | None = None
    diagnostics: list[Diagnostic] = field(default_factory=list)


# file:line:col: message   OR   something at line:col
RE_GCC = re.compile(
    r"^(?P<file>[A-Za-z]:[^:\n]+?|[^:\n]+?):(?P<line>\d+):(?:(?P<col>\d+):)?\s*(?P<msg>.+)$"
)
RE_AT = re.compile(r"\bat\s+(?P<line>\d+):(?P<col>\d+)\b")


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def find_podexc(root: Path | None = None) -> Path | None:
    root = root or project_root()
    candidates = [
        root / "build" / "podexc.exe",
        root / "build" / "Release" / "podexc.exe",
        root / "build" / "Debug" / "podexc.exe",
        root / "build" / "podexc",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def find_gxx() -> str | None:
    which = shutil.which("g++")
    if which:
        return which
    winget = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if winget.is_dir():
        for p in winget.rglob("g++.exe"):
            return str(p)
    return None


def ensure_mingw_on_path() -> None:
    gxx = find_gxx()
    if not gxx:
        return
    bin_dir = str(Path(gxx).parent)
    path = os.environ.get("PATH", "")
    if bin_dir.lower() not in path.lower():
        os.environ["PATH"] = bin_dir + os.pathsep + path


def parse_diagnostics(text: str, fallback_file: Path | None = None) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    seen: set[tuple[str, int, int, str]] = set()

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Strip "podexc error: " prefix
        if line.lower().startswith("podexc error:"):
            line = line.split(":", 1)[1].strip()

        m = RE_GCC.match(line)
        if m and m.group("file") and not m.group("file").lower().startswith("podexc"):
            f = m.group("file").strip()
            # Avoid matching "1> Compiling..." style
            if f.endswith(".pdx") or f.endswith(".cpp") or "\\" in f or "/" in f:
                path = Path(f)
                d = Diagnostic(
                    path=path if path.suffix else fallback_file,
                    line=int(m.group("line")),
                    col=int(m.group("col") or 1),
                    message=m.group("msg").strip(),
                    raw=raw_line,
                )
                key = (str(d.path), d.line, d.col, d.message)
                if key not in seen:
                    seen.add(key)
                    diags.append(d)
                continue

        m2 = RE_AT.search(line)
        if m2 and ("error" in line.lower() or "expected" in line.lower() or "unexpected" in line.lower()
                   or "unterminated" in line.lower() or "unknown" in line.lower()
                   or "cannot" in line.lower() or "module" in line.lower()
                   or "got '" in line.lower()):
            d = Diagnostic(
                path=fallback_file,
                line=int(m2.group("line")),
                col=int(m2.group("col")),
                message=line,
                raw=raw_line,
            )
            key = (str(d.path), d.line, d.col, d.message)
            if key not in seen:
                seen.add(key)
                diags.append(d)

    return diags


def build_pdx(source: Path, root: Path | None = None) -> BuildResult:
    root = root or project_root()
    source = source.resolve()
    log_lines: list[str] = []

    podexc = find_podexc(root)
    if not podexc:
        return BuildResult(
            False,
            "podexc.exe not found.\n"
            "Build the compiler first:\n"
            '  cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release\n'
            "  cmake --build build\n",
        )

    ensure_mingw_on_path()
    gxx = find_gxx()
    if not gxx:
        return BuildResult(False, "g++ not found. Install MinGW-w64 / WinLibs and add it to PATH.\n")

    out_dir = root / "build" / "studio_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    name = source.stem
    cpp_path = out_dir / f"{name}.cpp"
    exe_path = out_dir / f"{name}.exe"

    log_lines.append(f"------ Build started: {source.name} ------")
    log_lines.append("1> Compiling with podexc...")

    cmd1 = [str(podexc), str(source), "-o", str(cpp_path), "--stdlib", str(root / "stdlib")]
    cmd1 += ["-I", str(source.parent), "-I", str(root / "examples")]

    r1 = subprocess.run(
        cmd1, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(root)
    )
    log_lines.append(r1.stdout)
    if r1.stderr:
        log_lines.append(r1.stderr)
    if r1.returncode != 0:
        log = "\n".join(log_lines).strip() + "\n"
        log += "========== Build: 0 succeeded, 1 failed ==========\n"
        diags = parse_diagnostics(r1.stderr + "\n" + r1.stdout, source)
        return BuildResult(False, log, cpp_path=cpp_path, diagnostics=diags)

    log_lines.append(f"1> {source.name} -> {cpp_path.name}")
    log_lines.append("1> Linking with g++...")

    cmd2 = [gxx, "-std=c++17", "-O2", "-finput-charset=UTF-8", "-fexec-charset=UTF-8",
            str(cpp_path), "-o", str(exe_path)]
    r2 = subprocess.run(
        cmd2, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(root)
    )
    if r2.stdout:
        log_lines.append(r2.stdout)
    if r2.stderr:
        log_lines.append(r2.stderr)
    if r2.returncode != 0:
        log = "\n".join(log_lines).strip() + "\n"
        log += "========== Build: 0 succeeded, 1 failed ==========\n"
        diags = parse_diagnostics(r2.stderr + "\n" + r2.stdout, cpp_path)
        return BuildResult(False, log, cpp_path=cpp_path, diagnostics=diags)

    log_lines.append(f"1> {exe_path}")
    log_lines.append("========== Build: 1 succeeded, 0 failed ==========")
    return BuildResult(True, "\n".join(log_lines).strip() + "\n", exe_path=exe_path, cpp_path=cpp_path)


def run_exe(exe: Path, timeout: float = 30.0) -> BuildResult:
    if not exe.is_file():
        return BuildResult(False, f"Executable not found: {exe}\n")
    ensure_mingw_on_path()
    log_lines = [f"------ Run: {exe.name} ------"]
    try:
        r = subprocess.run(
            [str(exe)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=str(exe.parent),
        )
        if r.stdout:
            log_lines.append(r.stdout.rstrip("\n"))
        if r.stderr:
            log_lines.append(r.stderr.rstrip("\n"))
        log_lines.append(f"------ Process exited with code {r.returncode} ------")
        return BuildResult(r.returncode == 0, "\n".join(log_lines) + "\n", exe_path=exe)
    except subprocess.TimeoutExpired:
        return BuildResult(False, "\n".join(log_lines) + "\nProgram timed out.\n", exe_path=exe)
