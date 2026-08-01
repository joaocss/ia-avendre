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
  palavra-chave** (TF-IDF simples/full-text search) que funciona offline/sem chave.
- **Scraping proprio** do portal Freshdesk (nao ha API publica autenticada).
- **Dois fluxos paralelos** (ver detalhe abaixo): o local (arquivos + CLI, usado pela
  skill) e o de banco de dados (Supabase + API FastAPI em Docker, multi-tenant, com
  cache e metricas de uso). Nenhum dos dois depende do outro para funcionar.

Fluxo local (CLI/skill):
```
pergunta -> rag/buscar.py (semantico OU palavra-chave) -> artigos relevantes
        -> skill suporte-avendre monta resposta didatica multimodal + Fontes
```

Fluxo de banco (API, multi-tenant):
```
scraper/raspar_base.py -> base_conhecimento/artigos/*.md
        -> scripts/migrar_para_supabase.py -> Supabase (artigos/trechos + pgvector)
                                                         |
POST /perguntar (api/) -> cache_respostas (hit?) -> busca vetorial (pgvector)
        -> grava metrica em `perguntas` (empresa_id/usuario_id) -> resposta
GET /admin/metricas -> contagem de perguntas por empresa/usuario
```
- Tenant (`empresas`/`usuarios`) criado do zero no Supabase por enquanto (sem SSO real
  com CV CRM/Avendre ainda); ha um campo `id_externo_cvcrm` reservado para o
  mapeamento futuro.
- Ver plano detalhado (schema, decisoes, verificacao) em
  `C:\Users\JOAOSA\.claude\plans\refactored-drifting-shore.md`.

## Estrutura

```
ia-avendre/
├── CLAUDE.md                    # este arquivo
├── README.md                   # guia de uso
├── requisitos.txt              # deps: openai, fastapi, psycopg, pgvector, etc.
├── .env / .env.example          # OPENAI_API_KEY, DATABASE_URL, chaves Supabase (.env FORA do git)
├── .gitignore                  # ignora .env, chaves, indice_embeddings.json
├── scraper/
│   └── raspar_base.py          # raspa TODA a base -> base_conhecimento/
├── rag/
│   ├── construir_indice.py     # gera embeddings OpenAI -> indice_embeddings.json (local)
│   └── buscar.py               # busca semantica + fallback palavra-chave (CLI --k --json)
├── base_conhecimento/
│   ├── artigos/<id>-<slug>.md  # 1 markdown por artigo, com frontmatter (imagens/videos)
│   ├── manifesto.json          # indice de metadados de todos os artigos
│   └── indice_embeddings.json  # vetores (gerado; FORA do git)
├── db/
│   └── esquema.sql             # schema Supabase: empresas/usuarios/artigos/trechos/perguntas/cache_respostas
├── scripts/
│   └── migrar_para_supabase.py # migra base_conhecimento/*.md -> Supabase (idempotente)
├── api/                        # API FastAPI multi-tenant (cache + metricas)
│   ├── principal.py, banco.py, busca.py, esquemas.py
│   ├── rotas_perguntas.py      # POST /perguntar
│   └── rotas_admin.py          # GET /admin/metricas
├── Dockerfile, docker-compose.yml, .dockerignore
└── skill/suporte-avendre/
    └── SKILL.md                # a "IA de suporte" (orquestra o pipeline local)
```

## Comandos

```bash
# --- fluxo local (CLI/skill) ---
pip install -r requisitos.txt
python scraper/raspar_base.py                                            # ~120 artigos, 12 pastas
python rag/construir_indice.py                                           # precisa OPENAI_API_KEY no .env
python rag/buscar.py "como consultar meu extrato no avendre pay" --k 4 --json

# --- fluxo de banco (API multi-tenant) ---
# 1. rodar db/esquema.sql no SQL editor do Supabase
# 2. definir DATABASE_URL no .env (ja tem OPENAI_API_KEY)
python scripts/migrar_para_supabase.py
docker compose up --build
curl -X POST localhost:8000/perguntar -H "Content-Type: application/json" \
  -d '{"empresa_nome":"Teste","usuario_email":"a@a.com","pergunta":"..."}'
curl localhost:8000/admin/metricas
```

## Convencoes de codigo

- **Nomenclatura em portugues sem acentos**, seguindo o case da linguagem
  (snake_case em Python). Mantido em todo o projeto (variaveis, funcoes, arquivos).
- Comentarios em portugues.
- Scripts CLI usam `argparse` e imprimem JSON quando `--json`.

## Estado atual

- Fluxo local **validado ponta a ponta**: `base_conhecimento/` tem os **120 artigos
  completos** (raspagem corrigida — os seletores CSS do scraper estavam desatualizados
  e nao extraiam nenhum corpo; ver historico) + `manifesto.json` + indice semantico
  (`indice_embeddings.json`, 377 trechos) gerado e testado com sucesso.
- Fluxo de banco (Supabase + API): schema, script de migracao, API FastAPI e Docker
  foram criados (ver plano em `C:\Users\JOAOSA\.claude\plans\refactored-drifting-shore.md`).
  **Pendente**: aplicar `db/esquema.sql` no Supabase, rodar a migracao e testar a API
  ponta a ponta (schema/migracao/Docker ja escritos, falta validar em execucao).

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

- **NUNCA** commitar `OPENAI_API_KEY`, `DATABASE_URL` (tem a senha do Postgres) ou
  qualquer chave. Tudo isso vive so no `.env` local (ignorado pelo git).
- O `indice_embeddings.json` fica fora do git (`.gitignore`).
- Chaves compartilhadas em chat/sessoes anteriores (OpenAI e a senha do Supabase)
  ja foram expostas e devem ser **rotacionadas/resetadas** nos respectivos paineis
  assim que possivel — reusar uma chave ja exposta em chat nao remove a exposicao.
- `/admin/metricas` (na API) ainda **nao tem autenticacao** — nao expor publicamente
  sem adicionar isso antes.

## Roadmap / proximos passos

1. Aplicar `db/esquema.sql`, rodar `scripts/migrar_para_supabase.py` e validar a API
   ponta a ponta (cache, metricas, busca vetorial) — ver plano salvo.
2. Avaliar qualidade das respostas em perguntas reais; ajustar `TAMANHO_CHUNK`/`--k`.
3. Decidir hospedagem de producao do container da API (ainda em aberto).
4. Ligar o fluxo da skill (`SKILL.md`) na API em vez do CLI local, quando a hospedagem
   for decidida.
5. Autenticacao real (SSO Avendre/CV CRM) para substituir `empresa_nome`/`usuario_email`
   digitados, e proteger `/admin/metricas`.
6. Agendar re-scraping periodico para manter a base atualizada.

## Referencia

Projeto de padrao/inspiracao: ENEM em
`C:\Users\JOAOSA\Claude\Projects\ENEM\SaaS_Escolar_IA` (detalhes a alinhar).
