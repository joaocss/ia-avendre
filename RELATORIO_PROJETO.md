# Relatório do Projeto — ia-avendre

**Data do relatório:** 01/08/2026
**Repositório:** https://github.com/joaocss/ia-avendre (branch `main`)
**Último commit:** `61187f5` — "Renderiza artigo completo, feedback do usuario e metricas de satisfacao"
**Pasta local:** `C:\Users\JOAOSA\Claude\Projects\AVENDRE`

Planilha complementar: [mapeamento_projeto.xlsx](mapeamento_projeto.xlsx) (componentes,
banco de dados, tecnologias e dados de teste em formato tabular).

---

## 1. Resumo executivo

O `ia-avendre` é a IA de suporte multimodal da Avendre. A partir da documentação oficial
(`ajuda.avendre.com.br`), o sistema responde dúvidas sobre Avendre Vitrine, Gestão de
Parcerias, Avendre Pay e FAQ, de forma didática, com artigo completo, imagens e link
oficial. Hoje o projeto tem **dois fluxos funcionando em paralelo**:

1. **Fluxo local (CLI + skill do Claude)** — arquivos `.md` locais, índice de embeddings
   local, usado pela skill `suporte-avendre` instalada na conta do usuário.
2. **Fluxo de banco de dados (API multi-tenant)** — Supabase (Postgres + pgvector) como
   fonte de verdade, API em FastAPI rodando em Docker, com cache de respostas, métricas
   de uso por empresa/usuário, observabilidade via Datadog, e uma página de teste (`/chat`)
   com explicação gerada por IA, artigo completo renderizado e feedback do usuário.

Os dois fluxos são independentes — nenhum depende do outro para funcionar.

---

## 2. Arquitetura

```
                          ┌─────────────────────────────┐
                          │   ajuda.avendre.com.br        │
                          │  (Freshdesk, 120 artigos,     │
                          │   12 pastas, 4 categorias)    │
                          └───────────────┬───────────────┘
                                          │ scraper/raspar_base.py
                                          ▼
                          base_conhecimento/artigos/*.md
                          (120 arquivos, frontmatter c/ imagens/videos)
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                             ▼
      FLUXO LOCAL (CLI/skill)                       FLUXO DE BANCO (API)
      rag/construir_indice.py                       scripts/migrar_para_supabase.py
      -> indice_embeddings.json (377 trechos)        -> Supabase (artigos + trechos c/ pgvector)
                    │                                             │
                    ▼                                             ▼
      rag/buscar.py (CLI, --json)                   api/ (FastAPI, Docker)
      chamado por skill/suporte-avendre/SKILL.md       POST /perguntar
                                                        POST /perguntar/{id}/feedback
                                                        GET  /admin/metricas
                                                        GET  /admin/metricas-satisfacao
                                                        GET  /admin/metricas-infra (Datadog)
                                                        GET  /chat (pagina de teste)
                                                             │
                                                             ▼
                                                  Datadog Agent (container irmao)
                                                  APM (ddtrace) + infra + logs
```

---

## 3. Linha do tempo (commits)

| Commit | O que entregou |
|---|---|
| `3696f1a` | Primeiro commit — scraper, RAG local, skill, 5 artigos-seed |
| `ace2e24` | Raspagem completa (120 artigos), correção de bugs do scraper, schema Supabase, script de migração, API FastAPI inicial, Dockerfile/docker-compose |
| `b811283` | Observabilidade via Datadog (Agent + APM + `/admin/metricas-infra`) |
| `ace8355` | Correção do bug de busca vetorial (índice `ivfflat` aproximado), explicação gerada por IA, página `/chat` |
| `61187f5` | Artigo completo renderizado, feedback do usuário, métricas de satisfação (`/admin/metricas-satisfacao`) |

---

## 4. Tecnologias e ferramentas usadas

| Categoria | Tecnologia | Uso no projeto |
|---|---|---|
| Linguagem | Python 3.12/3.13 | Todo o backend (scraper, RAG, API) |
| Scraping | `requests`, `beautifulsoup4`, `html2text` | `scraper/raspar_base.py` — extrai artigos do Freshdesk |
| IA / LLM | OpenAI API (`text-embedding-3-small`, `gpt-4o-mini`) | Embeddings semânticos e geração da explicação didática |
| Framework web | FastAPI + Uvicorn | API (`api/`) |
| Banco de dados | Supabase (Postgres gerenciado) + extensão `pgvector` | Base de conhecimento, multi-tenant, cache, métricas |
| Driver de banco | `psycopg` 3 (+ `psycopg-pool`) | Conexão da API com o Postgres |
| Containers | Docker + Docker Compose | Empacota e roda a API + Agent do Datadog |
| Observabilidade | Datadog (Agent, APM/`ddtrace`, Metrics API) | Infra do container, traces, métricas de volta pro admin |
| Frontend (teste) | HTML/CSS/JS puro + `marked.js` (CDN) | Página `/chat`, renderização de markdown |
| Config/segredos | `python-dotenv`, arquivo `.env` (fora do git) | Chaves e credenciais |
| Versionamento | Git + GitHub | https://github.com/joaocss/ia-avendre |

---

## 5. Banco de dados (Supabase/Postgres)

Schema completo em [`db/esquema.sql`](db/esquema.sql). Estado atual (01/08/2026):

| Tabela | Registros | Para que serve |
|---|---|---|
| `artigos` | 120 | Base de conhecimento completa (título, categoria, pasta, url, markdown completo, imagens/vídeos) |
| `trechos` | 377 | Pedaços (chunks) de cada artigo + embedding (`vector(1536)`) para busca semântica |
| `empresas` | 9 | Tenants (todas de teste até agora — ver seção 7) |
| `usuarios` | 9 | Usuários vinculados a uma empresa |
| `perguntas` | 21 | Log de cada interação: pergunta, método usado, se veio do cache, feedback, se ficou sem resposta satisfatória |
| `cache_respostas` | 4 (variável) | Respostas já geradas, para não recalcular pergunta repetida |

Distribuição dos 120 artigos por categoria: Dúvidas Frequentes (62), Avendre Pay (33),
Avendre | Vitrine (20), Avendre | Gestão de Parcerias (5).

Colunas de controle notáveis em `perguntas`:
- `feedback` (`util` / `nao_util` / vazio) — o que o usuário achou da resposta.
- `sem_resposta` (booleano) — heurística (score de similaridade < 0.55) indicando que a
  base provavelmente não cobre bem aquele tema; usado para saber que conteúdo produzir.
- `escalonado_humano` (booleano, sempre `false` hoje) — reservado para a futura opção de
  transferir a conversa para um atendente humano.

---

## 6. Onde encontrar cada coisa (componentes)

Ver também a aba "Componentes" da planilha [mapeamento_projeto.xlsx](mapeamento_projeto.xlsx)
para os links diretos no GitHub.

- **Scraper**: [`scraper/raspar_base.py`](scraper/raspar_base.py)
- **RAG local (CLI)**: [`rag/construir_indice.py`](rag/construir_indice.py), [`rag/buscar.py`](rag/buscar.py)
- **Skill do Claude**: [`skill/suporte-avendre/SKILL.md`](skill/suporte-avendre/SKILL.md)
- **Schema do banco**: [`db/esquema.sql`](db/esquema.sql)
- **Script de migração**: [`scripts/migrar_para_supabase.py`](scripts/migrar_para_supabase.py)
- **API**: pacote [`api/`](api/) — `principal.py` (app), `banco.py` (acesso ao Postgres),
  `busca.py` (lógica de busca), `gerar_resposta.py` (explicação via IA), `rotas_perguntas.py`,
  `rotas_admin.py`, `datadog_cliente.py`, `esquemas.py` (modelos Pydantic)
- **Página de teste**: [`api/estaticos/chat.html`](api/estaticos/chat.html) — `http://localhost:8000/chat`
- **Docker**: [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml)
- **Documentação**: [`README.md`](README.md), [`CLAUDE.md`](CLAUDE.md)

### Endpoints da API (com o `docker compose` rodando localmente)

| Endpoint | Método | Descrição |
|---|---|---|
| `/chat` | GET | Página de teste manual (não é a interface final) |
| `/perguntar` | POST | Pergunta -> busca + explicação da IA + artigo completo |
| `/perguntar/{id}/feedback` | POST | Registra se a resposta ajudou (`{"util": true/false}`) |
| `/admin/metricas` | GET | Perguntas por empresa/usuário |
| `/admin/metricas-satisfacao` | GET | Resolvidas pela IA, sem resposta, feedback positivo/negativo |
| `/admin/metricas-infra` | GET | CPU/memória do container (via Datadog) |
| `/saude` | GET | Health check |
| `/docs` | GET | Swagger (documentação interativa da API) |

---

## 7. Acesso de teste

**Importante: o sistema hoje não tem autenticação.** `empresa_nome` e `usuario_email` são
apenas texto livre enviado em cada chamada para `/perguntar` — não existe cadastro, login
nem senha. Qualquer valor é aceito e vira uma linha nas tabelas `empresas`/`usuarios` na
primeira vez que aparece. Por isso não há "senha de teste" para listar.

Identificadores usados durante os testes desta sessão (dados de exemplo, sem sensibilidade):

| Empresa | E-mail |
|---|---|
| Imobiliaria Teste | corretor@teste.com |
| Incorporadora XPTO | gestor@xpto.com |
| Demo Swagger | teste@swagger.com |
| Teste manual / Teste Explicacao / Teste Fix / Teste Final / Teste Final2 / Teste Fase2 | teste@avendre.com |

Uma autenticação real (SSO com Avendre/CV CRM) é um item pendente do roadmap — ver
`CLAUDE.md`, seção "Roadmap / próximos passos".

---

## 8. Credenciais e segredos (o que existe, sem os valores)

Por segurança, **nenhum valor de senha, chave de API ou token está neste relatório**.
Todos os segredos ficam só no arquivo `.env` local (fora do git, listado no `.gitignore`).
O que existe hoje:

| Variável | Para que serve | Onde configurar |
|---|---|---|
| `OPENAI_API_KEY` | Embeddings + geração da explicação (LLM) | `.env` |
| `DATABASE_URL` | Conexão com o Postgres do Supabase (contém a senha do banco) | `.env` |
| `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Referência do projeto Supabase (a publishable key é pública por natureza) | `.env` |
| `DD_API_KEY` | Agent do Datadog envia métricas/logs/traces | `.env` |
| `DD_APP_KEY` / `DD_PAT` | Consultar a API do Datadog de volta (usado em `/admin/metricas-infra`) | `.env` |

Reforço: algumas dessas chaves foram coladas em texto puro no chat durante a sessão e já
foram tratadas como potencialmente expostas — se ainda não foram rotacionadas/resetadas
nos respectivos painéis (OpenAI, Supabase, Datadog), recomendo fazer isso.

---

## 9. Pendências / próximos passos

1. Autenticação real (SSO Avendre/CV CRM) no lugar de `empresa_nome`/`usuario_email` digitados.
2. Proteger `/admin/*` com autenticação (hoje são endpoints internos sem proteção).
3. Decidir hospedagem de produção do container (hoje só roda local via Docker Desktop).
4. Ligar a skill (`SKILL.md`) na API, quando a hospedagem for decidida.
5. API real de "falar com humano" (hoje só a coluna `perguntas.escalonado_humano` existe, reservada).
6. Dashboard visual do admin (hoje as rotas `/admin/*` devolvem JSON puro).
7. Interface com a identidade visual do Portal do Cliente (ainda não iniciada — precisa dos assets de design da Avendre).
