-- Esquema do banco (Supabase/Postgres) do ia-avendre
-- Cobre: base de conhecimento (artigos + embeddings) e metricas de uso multi-tenant
-- (empresas/usuarios) + cache de respostas.
--
-- Uso: rode este arquivo no SQL editor do Supabase (ou via psql usando a
-- DATABASE_URL do .env).

create extension if not exists vector;
create extension if not exists pgcrypto; -- gen_random_uuid()

-- ---------- multi-tenant ----------

create table if not exists empresas (
    id uuid primary key default gen_random_uuid(),
    nome text not null,
    id_externo_cvcrm text null,  -- reservado para o mapeamento futuro com o CV CRM
    criado_em timestamptz not null default now()
);

create table if not exists usuarios (
    id uuid primary key default gen_random_uuid(),
    empresa_id uuid not null references empresas(id) on delete cascade,
    email text not null,
    nome text null,
    id_externo_cvcrm text null,  -- reservado para o mapeamento futuro com o CV CRM
    criado_em timestamptz not null default now(),
    unique (empresa_id, email)
);

-- ---------- base de conhecimento ----------

create table if not exists artigos (
    id text primary key,  -- mesmo id numerico do Freshdesk (frontmatter dos .md)
    titulo text not null,
    categoria text not null,
    produto text not null,
    pasta text not null,
    url text not null,
    imagens jsonb not null default '[]',
    videos jsonb not null default '[]',
    conteudo_markdown text not null,
    atualizado_em timestamptz not null default now()
);

create table if not exists trechos (
    id bigserial primary key,
    artigo_id text not null references artigos(id) on delete cascade,
    n_trecho int not null,
    trecho text not null,
    embedding vector(1536),
    criado_em timestamptz not null default now(),
    unique (artigo_id, n_trecho)
);

-- lists baixo pois a base tem poucas centenas de trechos hoje; aumentar conforme crescer
create index if not exists trechos_embedding_idx
    on trechos using ivfflat (embedding vector_cosine_ops)
    with (lists = 10);

-- ---------- metricas + cache ----------

create table if not exists perguntas (
    id bigserial primary key,
    empresa_id uuid null references empresas(id) on delete set null,
    usuario_id uuid null references usuarios(id) on delete set null,
    pergunta text not null,
    metodo text not null,          -- 'semantica' ou 'palavra-chave'
    veio_do_cache boolean not null default false,
    criado_em timestamptz not null default now()
);

create index if not exists perguntas_empresa_idx on perguntas(empresa_id);
create index if not exists perguntas_usuario_idx on perguntas(usuario_id);

create table if not exists cache_respostas (
    chave text primary key,  -- sha256(pergunta normalizada + k)
    resposta jsonb not null,
    criado_em timestamptz not null default now()
);
