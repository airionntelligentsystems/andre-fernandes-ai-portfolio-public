"""Verificações delimitadas de publicação; não substituem auditoria de segurança."""

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
excluded = {".git", ".venv", "local", "__pycache__", ".pytest_cache"}
paths = [p for p in root.rglob("*") if p.is_file() and not excluded.intersection(p.relative_to(root).parts) and not any(part.endswith(".egg-info") for part in p.relative_to(root).parts)]
errors = []
checked_links = 0
patterns = [r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", r"gh[pousr]_[A-Za-z0-9]{30,}", r"AKIA[0-9A-Z]{16}", r"sk-[A-Za-z0-9_-]{30,}"]
for p in paths:
    if p.suffix not in {".md", ".py", ".json", ".jsonl", ".svg", ".yml", ".toml", ".lock"}:
        continue
    text = p.read_text(encoding="utf-8")
    if any(re.search(pattern, text) for pattern in patterns):
        errors.append(f"Padrão de credencial em {p.relative_to(root)}")
    if re.search(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/](?!/)", text):
        errors.append(f"Caminho absoluto de ambiente em {p.relative_to(root)}")
    if p.suffix == ".md":
        for href in re.findall(r"\]\(([^)]+)\)", text):
            if href.startswith(("https://", "http://", "mailto:", "#")):
                continue
            checked_links += 1
            target = href.split("#",1)[0]
            if target and not (p.parent/target).exists():
                errors.append(f"Link local ausente em {p.relative_to(root)}: {target}")
print(json.dumps({"files_reviewed": len(paths), "local_links_checked": checked_links, "errors": errors, "scope": "padrões selecionados de credenciais, caminhos locais e links; não auditoria completa"}, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)
