"""Gerar resumo sanitizado dos testes a partir de JUnit local."""

from datetime import datetime, timezone
from pathlib import Path
import importlib.metadata
import json
import platform
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
tree = ET.parse(root/"local/test-results.xml")
suites = list(tree.getroot().iter("testsuite"))
counts = {name: sum(int(s.get(name, "0")) for s in suites) for name in ["tests", "errors", "failures", "skipped"]}
if counts["errors"] or counts["failures"] or not counts["tests"]:
    raise SystemExit("Os testes não produziram evidência de aprovação")
report = {"scope": "testes locais do laboratório fictício", "generated_at": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(), "versions": {name: importlib.metadata.version(name) for name in ["pytest", "langgraph", "mcp", "pydantic"]}, **counts, "passed": counts["tests"]-counts["skipped"], "remote_ci_executed": False}
(root/"evidence/verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps(counts))
