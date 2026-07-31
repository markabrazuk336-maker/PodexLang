"""New PodexLang project templates."""

from __future__ import annotations

from pathlib import Path

MAIN_TEMPLATE = """# {name} — PodexLang project
#profit <io>
#profit <math>

fn main() -> int {{
    print("Welcome to {name}!")
    print("Edit main.pdx and press F5 to run.")

    let x = sqrt(64.0)
    print("sqrt(64) =")
    print(x)

    return 0
}}
"""

HELLO_TEMPLATE = """#profit <io>

fn main() -> int {{
    print("Hello, {name}!")
    return 0
}}
"""

TEMPLATES = {
    "Console App (io + math)": MAIN_TEMPLATE,
    "Hello only (io)": HELLO_TEMPLATE,
}


def create_project(parent_dir: Path, name: str, template_key: str) -> Path:
    """Create project folder with main.pdx. Returns path to main.pdx."""
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.strip())
    if not safe:
        raise ValueError("Project name is empty")

    root = parent_dir / safe
    if root.exists():
        raise FileExistsError(f"Folder already exists: {root}")

    root.mkdir(parents=True)
    tpl = TEMPLATES.get(template_key, MAIN_TEMPLATE)
    main = root / "main.pdx"
    main.write_text(tpl.format(name=safe), encoding="utf-8")

    # Tiny project marker for Studio
    (root / ".podexproj").write_text(
        f'{{"name": "{safe}", "main": "main.pdx"}}\n',
        encoding="utf-8",
    )
    return main
