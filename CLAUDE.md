# CLAUDE.md — Projeto ia-avendre

Arquivo de contexto para o **Claude Code**. Leia antes de qualquer tarefa neste
repositorio.

## O que e este projeto

IA de suporte multimodal da **Avendre** (estilo CVIA) que usa **RAG** para buscar na
documentacao oficial ([ajuda.avendre.com.br](https://ajuda.avendre.com.br/support/solutions))
e responder de forma **didatica, com link direto, imagens e videos** dos artigos.

Cobre 4 areas: **Avendre Vitrine**, **Gestao de Parcerias**, **Avendre Pay** e as
**Duvidas Frequentes (FAQ)**.

- Repo: https://github.com/joaocss/ia-avendre  (branch `main`)
- Pasta local: `C:\Users\JOAOSA\Claude\Projects\AVENDRE`

## Arquitetura (decisoes ja tomadas)

- **Entrega como skill do Claude** (`skill/suporte-avendre/SKILL.md`) que orquestra o
  fluxo. A skill tambem esta instalada na conta do usuario (persiste entre sessoes).
- **Embeddings OpenAI** `text-embedding-3-small` (semantico), com **fallback por
  palavra-chave** (TF-IDF simples) que funciona offline/sem chave.
- **Scraping proprio** do portal Freshdesk (nao ha API publica autenticada).

Fluxo:
```
pergunta -> rag/buscar.py (semantico OU palavra-chave) -> artigos relevantes
        -> skill suporte-avendre monta resposta didatica multimodal + Fontes
```

## Estrutura

```
ia-avendre/
├── CLAUDE.md                    # este arquivo
├── README.md                   # guia de uso
├── requisitos.txt              # deps: openai, requests, beautifulsoup4, html2text
├── .gitignore                  # ignora .env, chaves, indice_embeddings.json
├── scraper/
│   └── raspar_base.py          # raspa TODA a base -> base_conhecimento/
├── rag/
│   ├── construir_indice.py     # gera embeddings OpenAI -> indice_embeddings.json
│   └── buscar.py               # busca semantica + fallback palavra-chave (CLI --k --json)
├── base_conhecimento/
│   ├── artigos/<id>-<slug>.md  # 1 markdown por artigo, com frontmatter (imagens/videos)
│   ├── manifesto.json          # indice de metadados de todos os artigos
│   └── indice_embeddings.json  # vetores (gerado; FORA do git)
└── skill/suporte-avendre/
    └── SKILL.md                # a "IA de suporte" (orquestra o pipeline)
```

## Comandos

```bash
# 1. dependencias
pip install -r requisitos.txt

# 2. raspar toda a base (~120 artigos das 12 pastas). Teste: --limite 10
python scraper/raspar_base.py

# 3. gerar indice semantico (precisa da chave)
set OPENAI_API_KEY=sk-...        # Windows  (Linux/Mac: export)
python rag/construir_indice.py

# 4. buscar
python rag/buscar.py "como consultar meu extrato no avendre pay" --k 4 --json
```

## Convencoes de codigo

- **Nomenclatura em portugues sem acentos**, seguindo o case da linguagem
  (snake_case em Python). Mantido em todo o projeto (variaveis, funcoes, arquivos).
- Comentarios em portugues.
- Scripts CLI usam `argparse` e imprimem JSON quando `--json`.

## Estado atual

- Pipeline **validado ponta a ponta** (busca por palavra-chave retornando o artigo
  correto com imagens).
- `base_conhecimento/` tem **5 artigos-seed reais** (extrato web, primeiro acesso web
  Pay, login corretor, comissao/data, taxa de vendas) + `manifesto.json`.
- **Pendente (rodar na maquina do usuario):**
  1. `python scraper/raspar_base.py` para popular os ~120 artigos completos.
  2. `python rag/construir_indice.py` para gerar o indice semantico
     (a `api.openai.com` nao era alcancavel do ambiente anterior; na maquina do Joao e).

## Git (importante)

O Git deve ser rodado **nativo no Windows** (falha quando executado sobre a pasta
montada em sandbox). Se existir uma pasta `.git` parcial/quebrada, apague antes:

```bat
cd C:\Users\JOAOSA\Claude\Projects\AVENDRE
rmdir /s /q .git
git init
git add .
git commit -m "primeiro commit"
git branch -M main
git remote add origin https://github.com/joaocss/ia-avendre.git
git push -u origin main
```

## Seguranca

- **NUNCA** commitar `OPENAI_API_KEY`. Use variavel de ambiente ou `.env` (ignorado).
- O `indice_embeddings.json` fica fora do git (`.gitignore`).
- A chave usada nos primeiros testes foi compartilhada em chat e o repo e publico:
  **rotacionar essa chave** na plataforma da OpenAI.

## Roadmap / proximos passos

1. Rodar scraper completo + indice semantico.
2. Avaliar qualidade das respostas em perguntas reais; ajustar `TAMANHO_CHUNK`/`--k`.
3. (Opcional) Cache do embedding da consulta e reindexacao incremental.
4. (Opcional) Interface: CLI de chat ou pequeno app web sobre o `buscar.py`.
5. Agendar re-scraping periodico para manter a base atualizada.

## Referencia

Projeto de padrao/inspiracao: ENEM em
`C:\Users\JOAOSA\Claude\Projects\ENEM\SaaS_Escolar_IA` (detalhes a alinhar).
