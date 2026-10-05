"""Fixar versões observadas, sem incluir o caminho de instalação editável."""

from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
items = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines()
lines = [x for x in items if not x.startswith(("#", "-e")) and "andre-fernandes-portfolio-lab" not in x]
lines = [x+'; sys_platform == "win32"' if x.lower().startswith("pywin32==") else x for x in lines]
(root/"requirements.lock").write_text("\n".join(sorted(lines, key=str.lower))+"\n", encoding="utf-8")
print(f"Dependências fixadas: {len(lines)}")
