#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera a explicacao didatica complementar (LLM) a partir dos artigos recuperados,
seguindo as mesmas regras de skill/suporte-avendre/SKILL.md: responder so com
base no material fornecido, nunca inventar telas/passos, tom didatico em pt-BR.
"""

MODELO_RESPOSTA = "gpt-4o-mini"

PROMPT_SISTEMA = """Voce e a IA de suporte oficial da Avendre. Responda com base
EXCLUSIVAMENTE nos trechos de documentacao fornecidos, de forma didatica, clara e
em portugues do Brasil. Nunca invente telas, botoes ou passos que nao estejam no
material fornecido. Estruture a resposta assim: uma explicacao curta (1-3 frases)
e, quando fizer sentido, um passo a passo numerado. Nao inclua links de imagem
(markdown ![]()) nem uma secao de "Fontes" - isso e mostrado separadamente pela
interface. Se os trechos fornecidos nao cobrirem a pergunta, diga isso com
transparencia em vez de inventar."""


def gerar_explicacao(pergunta: str, artigos: list[dict]) -> str | None:
    if not artigos:
        return None
    try:
        from openai import OpenAI

        cliente = OpenAI()
        contexto = "\n\n---\n\n".join(
            f"Artigo: {a['titulo']}\n{a['trecho']}" for a in artigos
        )
        resposta = cliente.chat.completions.create(
            model=MODELO_RESPOSTA,
            messages=[
                {"role": "system", "content": PROMPT_SISTEMA},
                {"role": "user", "content": f"Pergunta do usuario: {pergunta}\n\nTrechos da documentacao:\n{contexto}"},
            ],
            temperature=0.3,
        )
        return resposta.choices[0].message.content
    except Exception:
        return None
