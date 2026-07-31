"""PodexCLI — command-line front-end for PodexLang."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

STUDIO_DIR = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("PODEX_ROOT", STUDIO_DIR.parent)).resolve()
if str(STUDIO_DIR) not in sys.path:
    sys.path.insert(0, str(STUDIO_DIR))

from build_service import build_pdx, ensure_mingw_on_path, find_gxx, find_podexc, project_root, run_exe


def cmd_version(_: argparse.Namespace) -> int:
    podexc = find_podexc(ROOT)
    gxx = find_gxx()
    print(f"PodexCLI 0.2.3")
    print(f"  root:   {ROOT}")
    print(f"  podexc: {podexc or '(not found)'}")
    print(f"  g++:    {gxx or '(not found)'}")
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    src = Path(args.file).resolve()
    if not src.is_file():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 1
    ensure_mingw_on_path()
    result = build_pdx(src, ROOT)
    print(result.log, end="")
    if result.ok and result.cpp_path:
        print(f"cpp: {result.cpp_path}")
        print(f"exe: {result.exe_path}")
    return 0 if result.ok else 1


def cmd_run(args: argparse.Namespace) -> int:
    src = Path(args.file).resolve()
    if not src.is_file():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 1
    ensure_mingw_on_path()
    built = build_pdx(src, ROOT)
    print(built.log, end="")
    if not built.ok or not built.exe_path:
        return 1
    ran = run_exe(built.exe_path)
    print(ran.log, end="")
    return 0 if ran.ok else 1


def cmd_studio(args: argparse.Namespace) -> int:
    app = ROOT / "studio" / "app.py"
    if not app.is_file():
        print(f"error: Studio not found at {app}", file=sys.stderr)
        return 1
    env = os.environ.copy()
    env["PODEX_ROOT"] = str(ROOT)
    bin_dir = str(ROOT / "bin")
    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
    cmd = [sys.executable.replace("python.exe", "pythonw.exe") if sys.executable.lower().endswith("python.exe") else sys.executable]
    # Prefer pythonw on Windows for GUI
    pyw = Path(sys.executable).with_name("pythonw.exe")
    if pyw.is_file():
        cmd = [str(pyw)]
    else:
        cmd = [sys.executable]
    cmd.append(str(app))
    if args.file:
        cmd.append(str(Path(args.file).resolve()))
    subprocess.Popen(cmd, cwd=str(ROOT), env=env)
    return 0


def cmd_podexc(args: argparse.Namespace) -> int:
    podexc = find_podexc(ROOT)
    if not podexc:
        print("error: podexc.exe not found", file=sys.stderr)
        return 1
    return subprocess.call([str(podexc), *args.args], cwd=str(ROOT))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="podex",
        description="PodexCLI — compile and run PodexLang (.pdx → C++ → exe)",
    )
    sub = p.add_subparsers(dest="command")

    sp = sub.add_parser("version", help="Show versions / toolchain")
    sp.set_defaults(func=cmd_version)

    sp = sub.add_parser("compile", aliases=["build", "c"], help="Compile .pdx to exe")
    sp.add_argument("file", help="Source .pdx file")
    sp.set_defaults(func=cmd_compile)

    sp = sub.add_parser("run", aliases=["r"], help="Compile and run .pdx")
    sp.add_argument("file", help="Source .pdx file")
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("studio", aliases=["ide"], help="Open Podex Studio")
    sp.add_argument("file", nargs="?", help="Optional .pdx to open")
    sp.set_defaults(func=cmd_studio)

    sp = sub.add_parser("raw", aliases=["podexc"], help="Call raw podexc compiler")
    sp.add_argument("args", nargs=argparse.REMAINDER, help="Arguments passed to podexc")
    sp.set_defaults(func=cmd_podexc)

    return p


def main(argv: list[str] | None = None) -> int:
    os.environ.setdefault("PODEX_ROOT", str(project_root()))
    argv = list(sys.argv[1:] if argv is None else argv)

    # Bare file: podex file.pdx  →  run
    if len(argv) == 1 and argv[0].lower().endswith(".pdx"):
        ns = argparse.Namespace(file=argv[0])
        return cmd_run(ns)

    parser = build_parser()
    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
