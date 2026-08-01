# ia-avendre

IA de suporte multimodal da **Avendre** que usa **RAG** para buscar na documentacao
oficial ([ajuda.avendre.com.br](https://ajuda.avendre.com.br/support/solutions)) e
responder de forma didatica, com **link direto, imagens e videos** dos artigos.

Inspirada no CVIA. Cobre **Avendre Vitrine**, **Gestao de Parcerias**, **Avendre Pay**
e as **Duvidas Frequentes**.

## Como funciona

```
Pergunta do usuario
      |
      v
[ rag/buscar.py ]  --  busca semantica (embeddings OpenAI) ou palavra-chave (fallback)
      |
      v
Artigos relevantes (titulo, link, imagens, videos, trecho)
      |
      v
[ skill suporte-avendre ]  --  monta resposta didatica multimodal + Fontes
```

## Estrutura

```
ia-avendre/
├── scraper/
│   └── raspar_base.py          # raspa TODA a base oficial -> base_conhecimento/
├── rag/
│   ├── construir_indice.py     # gera embeddings (OpenAI) -> indice_embeddings.json
│   └── buscar.py               # busca semantica + fallback por palavra-chave (local)
├── base_conhecimento/
│   ├── artigos/*.md            # um markdown por artigo (com frontmatter)
│   ├── manifesto.json          # indice de metadados de todos os artigos
│   └── indice_embeddings.json  # vetores (gerado; fora do git)
├── db/
│   └── esquema.sql             # schema do Supabase (artigos/trechos/empresas/etc)
├── scripts/
│   └── migrar_para_supabase.py # migra os .md + embeddings para o Supabase
├── api/                        # API FastAPI (multi-tenant, cache, metricas)
│   ├── principal.py            # app FastAPI (rotas + /saude)
│   ├── banco.py                # acesso ao Supabase (pool psycopg + pgvector)
│   ├── busca.py                # normalizacao, chave de cache, montagem de resultado
│   ├── esquemas.py             # modelos Pydantic
│   ├── rotas_perguntas.py      # POST /perguntar
│   └── rotas_admin.py          # GET /admin/metricas
├── skill/suporte-avendre/
│   └── SKILL.md                # orquestra o pipeline local (a "IA de suporte")
├── Dockerfile, docker-compose.yml  # container da API (aponta pro Supabase remoto)
├── requisitos.txt
└── README.md
```

## Passo a passo

### 1. Instalar dependencias
```bash
pip install -r requisitos.txt
```

### 2. Raspar toda a base (uma vez, ou para atualizar)
```bash
python scraper/raspar_base.py
```
Baixa os ~120 artigos das 12 pastas (Vitrine, Gestao de Parcerias, Avendre Pay, FAQ),
salva um `.md` por artigo com imagens/videos e gera o `manifesto.json`.

> Teste rapido: `python scraper/raspar_base.py --limite 10`

### 3. Gerar o indice semantico (embeddings OpenAI)
```bash
# Windows
set OPENAI_API_KEY=sk-...
python rag/construir_indice.py

# Linux/Mac
export OPENAI_API_KEY=sk-...
python rag/construir_indice.py
```
Usa `text-embedding-3-small`. Sem esta etapa, a busca funciona por palavra-chave.

### 4. Buscar
```bash
python rag/buscar.py "como consultar meu extrato no avendre pay" --k 4 --json
```

### 5. Usar como IA de suporte
A skill `skill/suporte-avendre/SKILL.md` orquestra tudo: recebe a pergunta, chama o
`buscar.py`, e monta a resposta didatica com link, imagens e video.

## Banco de dados (Supabase) + API (multi-tenant)

Alem do fluxo local acima (arquivos + CLI), o projeto tambem tem uma API real que
guarda a base de conhecimento e as metricas de uso num banco Postgres (Supabase),
com cache de respostas e contagem por empresa/usuario.

```bash
# 1. rode db/esquema.sql no SQL editor do Supabase (cria as tabelas + extensao pgvector)

# 2. defina OPENAI_API_KEY e DATABASE_URL no .env (ver .env.example)

# 3. migre os artigos + embeddings para o Supabase
python scripts/migrar_para_supabase.py

# 4. suba a API em Docker
docker compose up --build

# 5. teste
curl -X POST localhost:8000/perguntar \
  -H "Content-Type: application/json" \
  -d '{"empresa_nome":"Teste","usuario_email":"a@a.com","pergunta":"como troco minha senha do avendre pay"}'

curl localhost:8000/admin/metricas
```

Notas:
- `empresa_nome`/`usuario_email` sao apenas texto informado na chamada por enquanto —
  ainda **nao ha SSO real** com Avendre/CV CRM (fica para uma proxima etapa).
- `/admin/metricas` ainda **nao tem autenticacao** — e um endpoint interno.
- O fluxo local (`rag/buscar.py` + skill) continua funcionando normalmente e
  independente da API/Supabase.

## Observabilidade (Datadog, opcional)

O `docker-compose.yml` ja tem um servico `datadog` (o Agent) ao lado da API, com APM
(`ddtrace`) e coleta de logs/metricas de container prontos. Para ativar:

1. Crie/entre na conta em https://app.datadoghq.com/signup/setup e escolha
   **"Infraestrutura e aplicacoes de back-end"**.
2. Pegue a API key em Organization Settings -> API Keys e coloque em `DD_API_KEY`
   no `.env` (ver `.env.example`). Se sua conta for na regiao EU, ajuste tambem
   `DD_SITE` no `docker-compose.yml` (padrao e `datadoghq.com`).
3. `docker compose up --build -d` — o Agent sobe junto e passa a coletar
   metricas de infraestrutura, logs (stdout da API) e traces (APM) automaticamente.
4. Sem `DD_API_KEY`, o container `datadog` simplesmente nao inicia — a API continua
   funcionando normalmente (o Datadog e opcional, nao uma dependencia obrigatoria).

## Estado atual (seed)
A base ja vem com **5 artigos reais** de exemplo (extrato, primeiro acesso, login
corretor, comissao e taxa), suficientes para testar o fluxo ponta a ponta. Rode o
`raspar_base.py` para popular os ~120 artigos completos.

## Seguranca
- **Nunca** comite a `OPENAI_API_KEY`. Use variavel de ambiente ou um `.env` (ignorado pelo git).
- O `indice_embeddings.json` fica fora do git (ver `.gitignore`).

## Repositorio
https://github.com/joaocss/ia-avendre
