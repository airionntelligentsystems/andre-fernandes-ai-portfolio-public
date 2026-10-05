"""Servidor MCP oficial com ferramentas apenas demonstrativas."""

from mcp.server.mcpserver import MCPServer

from typing import Literal

from .contracts import Request, Source, StrictModel, Tenant
from .retrieval import KnowledgeBase

server = MCPServer("Laboratório de André Fernandes", version="0.1.0")
knowledge = KnowledgeBase()


class KnowledgeResult(StrictModel):
    sources: list[Source]
    corpus_version: str


class ProposalResult(StrictModel):
    status: Literal["proposal_only"]
    request_digest: str
    tenant: Tenant


@server.tool()
def search_knowledge(query: str, tenant: Tenant) -> KnowledgeResult:
    """Consultar conhecimento fictício do tenant validado e retornar fontes."""
    request = Request(query=query, tenant=tenant)
    return KnowledgeResult(sources=knowledge.search(request), corpus_version=knowledge.version)


@server.tool()
def propose_followup(query: str, tenant: Tenant) -> ProposalResult:
    """Preparar proposta fictícia para revisão, sem enviar ou registrar ação."""
    request = Request(query=query, tenant=tenant, intent="followup")
    return ProposalResult(status="proposal_only", request_digest=request.digest(), tenant=tenant)


if __name__ == "__main__":
    server.run(transport="stdio")
