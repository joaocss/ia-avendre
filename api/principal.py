#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API de suporte Avendre: monta o app FastAPI e registra as rotas."""

from dotenv import load_dotenv

load_dotenv()

import os

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .rotas_admin import roteador as roteador_admin
from .rotas_perguntas import roteador as roteador_perguntas

app = FastAPI(title="Suporte Avendre API", version="0.1.0")
app.include_router(roteador_perguntas)
app.include_router(roteador_admin)

PASTA_ESTATICOS = os.path.join(os.path.dirname(__file__), "estaticos")


@app.get("/saude")
def saude():
    return {"status": "ok"}


@app.get("/chat")
def chat():
    """Pagina de teste manual (chat) que consome o /perguntar - nao e a interface final."""
    return FileResponse(os.path.join(PASTA_ESTATICOS, "chat.html"))
