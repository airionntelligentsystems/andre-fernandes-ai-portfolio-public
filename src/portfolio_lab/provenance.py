"""Grafo estrutural de dependência com atualização atômica e impacto a jusante."""

from collections import deque


class DependencyGraph:
    def __init__(self):
        self.edges: dict[str, set[str]] = {}

    def descendants(self, node: str) -> list[str]:
        found: set[str] = set()
        queue = deque(self.edges.get(node, set()))
        while queue:
            current = queue.popleft()
            if current not in found:
                found.add(current)
                queue.extend(self.edges.get(current, set()))
        return sorted(found)

    def add(self, source: str, target: str) -> None:
        if source == target or source in self.descendants(target):
            raise ValueError("Dependência produziria ciclo")
        self.edges.setdefault(source, set()).add(target)
        self.edges.setdefault(target, set())

    def snapshot(self) -> dict[str, list[str]]:
        return {key: sorted(values) for key, values in sorted(self.edges.items())}
