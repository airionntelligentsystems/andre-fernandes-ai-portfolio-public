"""Preparação sintética para fine-tuning, sem treinamento ou provedor externo."""

import argparse
import hashlib
import json
import random
import re
import unicodedata
from pathlib import Path

from pydantic import Field

from .contracts import StrictModel


class Example(StrictModel):
    group: str = Field(min_length=1)
    messages: list[dict[str, str]]


def validate(example: Example) -> None:
    if [m.get("role") for m in example.messages] != ["system", "user", "assistant"]:
        raise ValueError("Sequência de mensagens inválida")
    for message in example.messages:
        if set(message) != {"role", "content"} or not message["content"].strip():
            raise ValueError("Mensagem sem contrato válido")
        text = message["content"]
        if re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|(?:\+?\d[\d ()-]{8,}\d)", text):
            raise ValueError("Identificador pessoal fora do dataset sintético permitido")


def fingerprint(example: Example) -> str:
    values = [unicodedata.normalize("NFKC", " ".join(m["content"].casefold().split())) for m in example.messages]
    return hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


def prepare(examples: list[Example], seed: int = 42):
    unique: dict[str, Example] = {}
    for example in examples:
        validate(example)
        key = fingerprint(example)
        if key in unique and unique[key].group != example.group:
            raise ValueError("Duplicata atribuída a grupos diferentes")
        unique.setdefault(key, example)
    groups = sorted({e.group for e in unique.values()})
    if len(groups) < 2:
        raise ValueError("São necessários pelo menos dois grupos independentes")
    random.Random(seed).shuffle(groups)
    train_groups = set(groups[:max(1, min(len(groups)-1, int(len(groups)*.7)))])
    train = [e for e in unique.values() if e.group in train_groups]
    validation = [e for e in unique.values() if e.group not in train_groups]
    report = {"input_examples": len(examples), "unique_examples": len(unique), "train_examples": len(train), "validation_examples": len(validation), "train_groups": sorted(train_groups), "validation_groups": sorted(set(groups)-train_groups), "seed": seed, "weights_trained": False}
    return train, validation, report


def synthetic_examples() -> list[Example]:
    groups = {
        "access": (["Como recupero o acesso?", "Preciso recuperar meu acesso."], "orientar_acesso"),
        "return": (["Qual é a regra de devolução?", "Onde consulto a devolução?"], "consultar_fonte"),
        "followup": (["Quero um follow-up.", "Pode propor continuidade?"], "propor_revisao"),
        "unknown": (["Há política sobre astronomia?", "Qual é a política de vulcões?"], "abster"),
        "status": (["O registro local foi aprovado?", "Como acompanho a proposta?"], "consultar_estado"),
        "handoff": (["Preciso falar com a equipe.", "Quero continuidade humana."], "encaminhar_equipe"),
    }
    return [Example(group=group, messages=[{"role": "system", "content": "Classifique a intenção do suporte fictício. Retorne somente o rótulo permitido."}, {"role": "user", "content": query}, {"role": "assistant", "content": label}]) for group, (queries, label) in groups.items() for query in queries]


def main():
    parser = argparse.ArgumentParser(description="Preparar datasets sintéticos para avaliação de fine-tuning")
    parser.add_argument("--output", type=Path, default=Path("evidence/datasets"))
    args = parser.parse_args()
    train, validation, report = prepare(synthetic_examples())
    args.output.mkdir(parents=True, exist_ok=True)
    for name, values in [("train", train), ("validation", validation)]:
        payload = "".join(json.dumps({"messages": e.messages}, ensure_ascii=False)+"\n" for e in values)
        (args.output/f"{name}.jsonl").write_text(payload, encoding="utf-8")
        report[f"{name}_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    (args.output/"report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))


if __name__ == "__main__":
    main()
