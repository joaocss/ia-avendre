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
│   └── buscar.py               # busca semantica + fallback por palavra-chave
├── base_conhecimento/
│   ├── artigos/*.md            # um markdown por artigo (com frontmatter)
│   ├── manifesto.json          # indice de metadados de todos os artigos
│   └── indice_embeddings.json  # vetores (gerado; fora do git)
├── skill/suporte-avendre/
│   └── SKILL.md                # orquestra o pipeline (a "IA de suporte")
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

## Estado atual (seed)
A base ja vem com **5 artigos reais** de exemplo (extrato, primeiro acesso, login
corretor, comissao e taxa), suficientes para testar o fluxo ponta a ponta. Rode o
`raspar_base.py` para popular os ~120 artigos completos.

## Seguranca
- **Nunca** comite a `OPENAI_API_KEY`. Use variavel de ambiente ou um `.env` (ignorado pelo git).
- O `indice_embeddings.json` fica fora do git (ver `.gitignore`).

## Repositorio
https://github.com/joaocss/ia-avendre
