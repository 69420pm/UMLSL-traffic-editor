import os
import subprocess
import sys
from pathlib import Path

# --- CONFIGURATION ---
# 1. Where your .ui and .qrc files live (and the 'icons' folder)
SEARCH_DIR = Path(".") / "qt_widgets"

# 2. Where you want the compiled .py files to go
OUTPUT_DIR = Path(".") / "compiled_widgets"

UIC_CMD = "pyside6-uic"
RCC_CMD = "pyside6-rcc"


def compile_project():
    print(f"--- Compiling UI Files ---")
    print(f"Source: {SEARCH_DIR}")
    print(f"Target: {OUTPUT_DIR}\n")

    # Check if source exists to prevent confusing errors
    if not SEARCH_DIR.exists():
        print(f"ERROR: Source directory '{SEARCH_DIR}' not found.")
        return

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create __init__.py so 'compiled_widgets' is treated as a python package
    (OUTPUT_DIR / "__init__.py").touch()

    # 1. Compile Resources (.qrc -> _rc.py)
    # We use .resolve() to get absolute paths, ensuring commands work
    # regardless of which folder we switch into.
    for qrc_file in SEARCH_DIR.rglob("*.qrc"):
        output_file = OUTPUT_DIR / f"{qrc_file.stem}_rc.py"

        if needs_compile(qrc_file, output_file):
            # We run the command INSIDE the qt_widgets folder (cwd=qrc_file.parent)
            # so that relative paths like "icons/image.svg" inside the .qrc file work.
            cmd = [RCC_CMD, qrc_file.name, "-o", str(output_file.resolve())]

            print(f"Compiling {qrc_file.name}...")
            try:
                subprocess.run(cmd, check=True, cwd=qrc_file.parent)
                print(" -> Success")
            except subprocess.CalledProcessError as e:
                print(f" -> ERROR: {e}")
        else:
            print(f"Skipped: {qrc_file.name} (up to date)")

    # 2. Compile UI Files (.ui -> ui_*.py)
    for ui_file in SEARCH_DIR.rglob("*.ui"):
        output_file = OUTPUT_DIR / f"ui_{ui_file.stem}.py"

        if needs_compile(ui_file, output_file):
            cmd = [UIC_CMD, str(ui_file), "-o", str(output_file)]
            print(f"Compiling {ui_file.name}...")
            try:
                subprocess.run(cmd, check=True)

                # 3. Patch Imports
                # Changes 'import resources_rc' to 'from . import resources_rc'
                fix_imports(output_file)
                print(" -> Success (imports patched)")

            except subprocess.CalledProcessError as e:
                print(f" -> ERROR: {e}")
        else:
            print(f"Skipped: {ui_file.name} (up to date)")


def needs_compile(source: Path, target: Path) -> bool:
    """Returns True if target doesn't exist or source is newer."""
    return not target.exists() or source.stat().st_mtime > target.stat().st_mtime


def fix_imports(py_file: Path):
    """
    Reads the generated python file and changes absolute imports
    of resource files to relative imports so they work within the package.
    """
    try:
        content = py_file.read_text(encoding='utf-8')

        # uic generates: import resources_rc
        # we need:       from . import resources_rc
        old_import = "import resources_rc"
        new_import = "from . import resources_rc"

        if old_import in content and new_import not in content:
            content = content.replace(old_import, new_import)
            py_file.write_text(content, encoding='utf-8')

    except Exception as e:
        print(f"Warning: Could not patch imports in {py_file.name}: {e}")


if __name__ == "__main__":
    compile_project()