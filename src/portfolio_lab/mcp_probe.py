"""Prova do transporte stdio e de chamadas MCP reais em subprocesso local."""

import asyncio
import json
import sys

from mcp import Client
from mcp.client.stdio import StdioServerParameters


async def probe() -> dict:
    params = StdioServerParameters(command=sys.executable, args=["-m", "portfolio_lab.mcp_server"])
    async with Client(params, read_timeout_seconds=10) as client:
        tools = await client.list_tools()
        names = sorted(t.name for t in tools.tools)
        if names != ["propose_followup", "search_knowledge"]:
            raise AssertionError("Catálogo MCP inesperado")
        found = await client.call_tool("search_knowledge", {"query": "devolução", "tenant": "demo_alpha"})
        sources = found.structured_content["sources"]
        if not sources or any(s["tenant"] != "demo_alpha" for s in sources):
            raise AssertionError("Recuperação MCP fora do contexto")
        proposal = await client.call_tool("propose_followup", {"query": "suporte", "tenant": "demo_alpha"})
        if proposal.structured_content["status"] != "proposal_only":
            raise AssertionError("Ferramenta não preservou o limite de proposta")
        invalid = await client.call_tool("search_knowledge", {"query": "devolução", "tenant": "real_client"})
        if not invalid.is_error:
            raise AssertionError("Tenant inválido não foi rejeitado")
        return {"transport": "stdio", "sdk": "mcp", "tools": names, "tenant_isolation": True, "invalid_tenant_rejected": True, "effect": "none", "status": "passed"}


def main():
    print(json.dumps(asyncio.run(probe()), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
