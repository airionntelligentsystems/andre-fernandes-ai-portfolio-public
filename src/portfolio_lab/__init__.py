"""Referência fictícia, com avaliações locais e sem inferência remota."""

import os

# O laboratório não envia traces para um serviço remoto.
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
