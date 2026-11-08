#!/usr/bin/env python3
"""Create and build one research report. Run from any directory."""
import argparse
import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["new", "build", "watch", "preview"])
    parser.add_argument("date", nargs="?", help="report date (YYYY-MM-DD)")
    parser.add_argument("--port", type=int, default=8000, help="preview HTTP port (default: 8000)")
    args = parser.parse_args()
    if not args.date:
        parser.error("date is required (YYYY-MM-DD)")
    try:
        day = datetime.date.fromisoformat(args.date)
    except ValueError:
        parser.error("invalid date; use YYYY-MM-DD")
    if day.isoformat() != args.date:
        parser.error("use YYYY-MM-DD")
    directory = ROOT / "reports" / str(day.year) / args.date
    source = directory / "main.tex"
    output = ROOT / "build" / args.date
    if args.action == "new":
        directory.parent.mkdir(parents=True, exist_ok=True)
        directory.mkdir()  # Refuse to overwrite an existing report.
        (directory / "images").mkdir()
        content = (ROOT / "template" / "report.tex").read_text()
        source.write_text(content.replace("@@DATE@@", f"{day.year}年{day.month}月{day.day}日"))
        print(source.relative_to(ROOT))
        return
    if not source.is_file():
        parser.error(f"file not found: {source}")
    if not shutil.which("latexmk"):
        parser.error("latexmk is missing; install it and add it to PATH (or run nix develop)")
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    # The final empty component retains TeX Live's standard search paths.
    for variable in ("TEXINPUTS", "BIBINPUTS", "BSTINPUTS"):
        env[variable] = f".:{ROOT}//:" + env.get(variable, "")
    command = ["latexmk", "-norc", "-r", str(ROOT / ".latexmkrc"),
               f"-outdir={output}"]
    if args.action == "watch":
        command.append("-pvc")
    command.append(source.name)
    if args.action == "preview":
        from preview import preview
        preview(command, source, output, env, ROOT, args.port)
        return
    subprocess.run(command, cwd=source.parent, env=env, check=True)
    print(output / (source.stem + ".pdf"))


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
