#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""API de suporte Avendre: monta o app FastAPI e registra as rotas."""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from .rotas_admin import roteador as roteador_admin
from .rotas_perguntas import roteador as roteador_perguntas

app = FastAPI(title="Suporte Avendre API", version="0.1.0")
app.include_router(roteador_perguntas)
app.include_router(roteador_admin)


@app.get("/saude")
def saude():
    return {"status": "ok"}
