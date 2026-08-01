#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raspador da Base de Conhecimento oficial da Avendre (Freshdesk).

Percorre todas as categorias e pastas da central de ajuda
(https://ajuda.avendre.com.br/support/solutions), baixa cada artigo,
converte o corpo para Markdown e extrai imagens e videos.

Saidas geradas em ../base_conhecimento:
  - artigos/<id>-<slug>.md   -> um arquivo por artigo (com frontmatter)
  - manifesto.json           -> indice de todos os artigos (metadados)

Uso:
  python raspar_base.py                 # raspa tudo
  python raspar_base.py --limite 10     # raspa apenas os 10 primeiros (teste)

Dependencias: requests, beautifulsoup4, html2text  (ver requisitos.txt)
"""

import argparse
import json
import os
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
import html2text

BASE = "https://ajuda.avendre.com.br"
PASTA_SAIDA = os.path.join(os.path.dirname(__file__), "..", "base_conhecimento")
PASTA_ARTIGOS = os.path.join(PASTA_SAIDA, "artigos")

# Mapa autoritativo das pastas da base (categoria -> pastas).
# Coletado da central de ajuda em 2026-08-01.
ESTRUTURA = [
    {"categoria": "Avendre | Vitrine", "produto": "vitrine", "pastas": [
        {"nome": "Duvidas de Acessos", "id": "157000939634"},
        {"nome": "Incorporadoras", "id": "157000939211"},
        {"nome": "Corretores e Imobiliarias", "id": "157000939366"},
    ]},
    {"categoria": "Avendre | Gestao de Parcerias", "produto": "gestao_parcerias", "pastas": [
        {"nome": "Gestao de Parcerias", "id": "157000939660"},
    ]},
    {"categoria": "Avendre Pay", "produto": "avendre_pay", "pastas": [
        {"nome": "Login", "id": "157000939091"},
        {"nome": "Multiplas Contas", "id": "157000939088"},
        {"nome": "Senha e PIN", "id": "157000939083"},
        {"nome": "Pix", "id": "157000939082"},
        {"nome": "Extratos", "id": "157000939092"},
        {"nome": "Configuracoes", "id": "157000941908"},
    ]},
    {"categoria": "Duvidas Frequentes", "produto": "faq", "pastas": [
        {"nome": "FAQ - Avendre Vitrine", "id": "157000939215"},
        {"nome": "FAQ - Avendre Pay", "id": "157000939217"},
    ]},
]

CABECALHOS = {"User-Agent": "Mozilla/5.0 (compatible; SuporteAvendreBot/1.0)"}

conversor = html2text.HTML2Text()
conversor.body_width = 0          # nao quebra linhas
conversor.ignore_links = False
conversor.ignore_images = False
conversor.protect_links = True


def buscar_html(url):
    resposta = requests.get(url, headers=CABECALHOS, timeout=30)
    resposta.raise_for_status()
    resposta.encoding = "utf-8"
    return resposta.text


def coletar_urls_de_artigos(pasta_id):
    """Percorre uma pasta (com paginacao) e retorna as URLs de todos os artigos."""
    urls = []
    pagina = 1
    while True:
        if pagina == 1:
            url_pasta = f"{BASE}/support/solutions/folders/{pasta_id}"
        else:
            url_pasta = f"{BASE}/support/solutions/folders/{pasta_id}/page/{pagina}"
        html = buscar_html(url_pasta)
        sopa = BeautifulSoup(html, "html.parser")
        encontrados = []
        for a in sopa.select("a[href*='/support/solutions/articles/']"):
            href = a.get("href", "")
            if "/articles/" in href:
                url_completa = urljoin(BASE, href.split("#")[0])
                if url_completa not in urls and url_completa not in encontrados:
                    encontrados.append(url_completa)
        urls.extend(encontrados)
        # ha proxima pagina?
        tem_proxima = sopa.find("a", string=re.compile(r"Pr[oó]ximo"))
        if not tem_proxima or not encontrados:
            break
        pagina += 1
        time.sleep(0.3)
    return urls


def extrair_corpo(sopa):
    """Localiza o elemento com o corpo do artigo, testando seletores comuns do Freshdesk."""
    for seletor in [
        "div.article-body", "#article-body", "article .article-body",
        "div.fw-article-content", "article", "div[itemprop='articleBody']",
    ]:
        elemento = sopa.select_one(seletor)
        if elemento and len(elemento.get_text(strip=True)) > 40:
            return elemento
    return None


def raspar_artigo(url):
    html = buscar_html(url)
    sopa = BeautifulSoup(html, "html.parser")

    # titulo
    meta_titulo = sopa.find("meta", property="og:title")
    titulo = meta_titulo["content"].strip() if meta_titulo and meta_titulo.get("content") else url

    # id do artigo (numero na URL)
    m = re.search(r"/articles/(\d+)", url)
    artigo_id = m.group(1) if m else str(abs(hash(url)))

    corpo = extrair_corpo(sopa)
    if corpo is None:
        return None

    # imagens e videos ANTES de converter (para nao perder src)
    imagens = []
    for img in corpo.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        if src.startswith("http") and src not in imagens:
            imagens.append(src)

    videos = []
    for tag in corpo.find_all(["iframe", "video", "source"]):
        src = tag.get("src") or ""
        if src.startswith("http") and src not in videos:
            videos.append(src)

    markdown = conversor.handle(str(corpo)).strip()

    # resumo: primeiro paragrafo de texto util
    texto_puro = corpo.get_text(" ", strip=True)
    resumo = re.sub(r"\s+", " ", texto_puro)[:320]

    return {
        "id": artigo_id,
        "titulo": titulo,
        "url": url,
        "resumo": resumo,
        "imagens": imagens,
        "videos": videos,
        "markdown": markdown,
    }


def slugificar(texto):
    texto = re.sub(r"[^\w\s-]", "", texto, flags=re.UNICODE).strip().lower()
    texto = re.sub(r"[\s_-]+", "-", texto)
    return texto[:80]


def salvar_artigo(artigo, categoria, produto, pasta):
    os.makedirs(PASTA_ARTIGOS, exist_ok=True)
    nome = f"{artigo['id']}-{slugificar(artigo['titulo'])}.md"
    caminho = os.path.join(PASTA_ARTIGOS, nome)
    frontmatter = [
        "---",
        f"id: {artigo['id']}",
        f"titulo: {json.dumps(artigo['titulo'], ensure_ascii=False)}",
        f"categoria: {json.dumps(categoria, ensure_ascii=False)}",
        f"produto: {produto}",
        f"pasta: {json.dumps(pasta, ensure_ascii=False)}",
        f"url: {artigo['url']}",
        f"imagens: {json.dumps(artigo['imagens'], ensure_ascii=False)}",
        f"videos: {json.dumps(artigo['videos'], ensure_ascii=False)}",
        "---",
        "",
        f"# {artigo['titulo']}",
        "",
        artigo["markdown"],
        "",
    ]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(frontmatter))
    return nome


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=0, help="limita quantidade de artigos (0 = todos)")
    parser.add_argument("--pausa", type=float, default=0.4, help="pausa entre requisicoes (s)")
    args = parser.parse_args()

    os.makedirs(PASTA_ARTIGOS, exist_ok=True)
    manifesto = []
    total = 0

    for cat in ESTRUTURA:
        for pasta in cat["pastas"]:
            print(f"\n== {cat['categoria']} / {pasta['nome']} ==")
            try:
                urls = coletar_urls_de_artigos(pasta["id"])
            except Exception as e:
                print(f"  [erro ao listar pasta {pasta['id']}] {e}")
                continue
            print(f"  {len(urls)} artigos encontrados")
            for url in urls:
                if args.limite and total >= args.limite:
                    break
                try:
                    artigo = raspar_artigo(url)
                    if not artigo:
                        print(f"  [sem corpo] {url}")
                        continue
                    nome = salvar_artigo(artigo, cat["categoria"], cat["produto"], pasta["nome"])
                    manifesto.append({
                        "id": artigo["id"],
                        "titulo": artigo["titulo"],
                        "categoria": cat["categoria"],
                        "produto": cat["produto"],
                        "pasta": pasta["nome"],
                        "url": artigo["url"],
                        "arquivo": f"artigos/{nome}",
                        "resumo": artigo["resumo"],
                        "imagens": artigo["imagens"],
                        "videos": artigo["videos"],
                    })
                    total += 1
                    print(f"  ok  {artigo['titulo'][:70]}")
                    time.sleep(args.pausa)
                except Exception as e:
                    print(f"  [erro] {url} -> {e}")
            if args.limite and total >= args.limite:
                break
        if args.limite and total >= args.limite:
            break

    with open(os.path.join(PASTA_SAIDA, "manifesto.json"), "w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)

    print(f"\nConcluido: {total} artigos salvos em {PASTA_ARTIGOS}")
    print(f"Manifesto: {os.path.join(PASTA_SAIDA, 'manifesto.json')}")


if __name__ == "__main__":
    main()
