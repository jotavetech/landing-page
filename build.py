#!/usr/bin/env python3
"""Gera o site estático da Jotave Tech em _site/.

Uso:
    pip install -r requirements.txt
    python3 build.py            # gera _site/
    python3 build.py --serve    # gera e abre um servidor local em http://localhost:8000

Conteúdo editável:
    content/site.json           informações da empresa, links das lojas, opções
    content/i18n/pt-br.json     textos em português
    content/i18n/en.json        textos em inglês (mesmas chaves do pt-br.json)
    content/legal/pt-br.json    políticas de privacidade e termos de uso de cada aplicativo
    content/legal/en.json       o mesmo, em inglês (mesmas chaves do pt-br.json)
"""

import datetime
import functools
import http.server
import json
import os
import posixpath
import re
import shutil
import sys

from markupsafe import Markup, escape
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "_site")

LANGS = ["pt-br", "en"]
DEFAULT_LANG = "pt-br"
APP_KEYS = ["gro", "balanca-diaria", "spokn"]

# Chave da página -> caminho em cada idioma (sempre terminando em "/").
ROUTES = {
    "home":           {"pt-br": "",                          "en": ""},
    "products":       {"pt-br": "produtos/",                 "en": "products/"},
    "gro":            {"pt-br": "produtos/gro/",             "en": "products/gro/"},
    "balanca-diaria": {"pt-br": "produtos/balanca-diaria/",  "en": "products/balanca-diaria/"},
    "spokn":          {"pt-br": "produtos/spokn/",           "en": "products/spokn/"},
    "solutions":      {"pt-br": "solucoes/",                 "en": "solutions/"},
    "about":          {"pt-br": "sobre/",                    "en": "about/"},
    "faq":            {"pt-br": "perguntas-frequentes/",     "en": "faq/"},
    "contact":        {"pt-br": "contato/",                  "en": "contact/"},
    "privacy":        {"pt-br": "politica-de-privacidade/",  "en": "privacy-policy/"},
    "terms":          {"pt-br": "termos-de-uso/",            "en": "terms-of-use/"},
}

# Política de privacidade e termos de uso de cada aplicativo, dentro da página do produto.
LEGAL_DOCS = {
    "privacy": {"pt-br": "politica-de-privacidade/", "en": "privacy-policy/"},
    "terms":   {"pt-br": "termos-de-uso/",           "en": "terms-of-use/"},
}
for _app in APP_KEYS:
    for _doc, _paths in LEGAL_DOCS.items():
        ROUTES[_app + "-" + _doc] = {l: ROUTES[_app][l] + _paths[l] for l in _paths}

TEMPLATES = {
    "home": "pages/home.html",
    "products": "pages/products.html",
    "gro": "pages/product.html",
    "balanca-diaria": "pages/product.html",
    "spokn": "pages/product.html",
    "solutions": "pages/solutions.html",
    "about": "pages/about.html",
    "faq": "pages/faq.html",
    "contact": "pages/contact.html",
    "privacy": "pages/legal.html",
    "terms": "pages/legal.html",
}
TEMPLATES.update({app + "-" + doc: "pages/app-legal.html" for app in APP_KEYS for doc in LEGAL_DOCS})

PLACEHOLDER_RE = re.compile(r"\[[^\[\]]+\]")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_same_shape(a, b, path="", errors=None):
    """Garante que pt-br.json e en.json tenham as mesmas chaves e listas do mesmo tamanho."""
    if errors is None:
        errors = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k.startswith("_"):
                continue
            if k not in a or k not in b:
                errors.append(f"{path}.{k}: existe só em {'pt-br' if k in a else 'en'}")
            else:
                check_same_shape(a[k], b[k], f"{path}.{k}", errors)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            errors.append(f"{path}: listas com tamanhos diferentes ({len(a)} x {len(b)})")
        for i, (x, y) in enumerate(zip(a, b)):
            check_same_shape(x, y, f"{path}[{i}]", errors)
    elif type(a) is not type(b):
        errors.append(f"{path}: tipos diferentes")
    return errors


def rich(text):
    """Escapa o texto e destaca trechos [entre colchetes] como campos a preencher."""
    if text is None:
        return Markup("")
    out, last = [], 0
    for m in PLACEHOLDER_RE.finditer(text):
        out.append(escape(text[last:m.start()]))
        out.append(Markup('<span class="ph">%s</span>') % m.group(0))
        last = m.end()
    out.append(escape(text[last:]))
    return Markup("").join(out)


LINK_RE = re.compile(r"(https?://[^\s<>()]+[^\s<>().,;:]|[\w.+-]+@[\w-]+(?:\.[\w-]+)+)")


def links(text):
    """Como rich(), e também transforma endereços de e-mail e URLs em links."""
    out, last = [], 0
    for m in LINK_RE.finditer(text or ""):
        out.append(rich(text[last:m.start()]))
        target = m.group(0)
        if "@" in target and not target.startswith("http"):
            out.append(Markup('<a href="mailto:%s">%s</a>') % (target, target))
        else:
            out.append(Markup('<a href="%s" target="_blank" rel="noopener">%s</a>') % (target, target))
        last = m.end()
    out.append(rich((text or "")[last:]))
    return Markup("").join(out)


def fmt(text, **kwargs):
    for k, v in kwargs.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def plain(text):
    """Remove os colchetes de marcadores (para atributos como alt e aria-label)."""
    return PLACEHOLDER_RE.sub("", text or "").strip()


def digits(text):
    return re.sub(r"\D", "", text or "")


def make_env():
    env = Environment(
        loader=FileSystemLoader(os.path.join(SRC, "templates")),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["rich"] = rich
    env.filters["fmt"] = fmt
    env.filters["links"] = links
    env.filters["plain"] = plain
    env.filters["digits"] = digits
    env.filters["tojson_attr"] = lambda v: json.dumps(v, ensure_ascii=False)

    svg_dir = os.path.join(SRC, "templates", "svg")

    @functools.lru_cache(maxsize=None)
    def svg(name):
        with open(os.path.join(svg_dir, name + ".svg"), encoding="utf-8") as f:
            return Markup(f.read())

    env.globals["svg"] = svg
    return env


def page_dir(lang, key):
    return lang + "/" + ROUTES[key][lang]


def relative(from_dir, to_path):
    """Caminho relativo entre a pasta da página atual e um destino (pasta 'x/' ou arquivo)."""
    rel = posixpath.relpath("/" + to_path, "/" + from_dir)
    if to_path.endswith("/"):
        rel = "./" if rel == "." else rel + "/"
    return rel


def build():
    site = load_json(os.path.join(CONTENT, "site.json"))
    strings = {lang: load_json(os.path.join(CONTENT, "i18n", lang + ".json")) for lang in LANGS}

    legal = {lang: load_json(os.path.join(CONTENT, "legal", lang + ".json")) for lang in LANGS}

    errors = check_same_shape(strings["pt-br"], strings["en"], "i18n")
    errors += check_same_shape(legal["pt-br"], legal["en"], "legal")
    if errors:
        sys.exit("Textos de tradução incompletos:\n  " + "\n  ".join(errors))

    year = datetime.date.today().year
    env = make_env()
    domain = site["domain"].rstrip("/")

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(SRC, "static"), os.path.join(OUT, "assets"))

    def write(rel_path, html):
        path = os.path.join(OUT, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    sitemap = []
    for lang in LANGS:
        t = strings[lang]
        for key, template in TEMPLATES.items():
            here = page_dir(lang, key)

            def url(target, target_lang=None, _here=here, _lang=lang):
                return relative(_here, page_dir(target_lang or _lang, target))

            def asset(path, _here=here):
                return relative(_here, "assets/" + path)

            alternates = {l: domain + "/" + page_dir(l, key) for l in LANGS}
            ctx = dict(
                t=t, site=site, lang=lang, langs=LANGS, page=key, year=year,
                url=url, asset=asset, app_keys=APP_KEYS,
                canonical=alternates[lang], alternates=alternates,
                other_lang=[l for l in LANGS if l != lang][0],
                strings=strings,
            )
            app_key, doc = key, ""
            if key not in APP_KEYS and key.rsplit("-", 1)[0] in APP_KEYS:
                app_key, doc = key.rsplit("-", 1)
            if app_key in APP_KEYS:
                ctx["app_key"] = app_key
                ctx["app"] = t["apps"][app_key]
                ctx["app_site"] = site["apps"][app_key]
                ctx["legal"] = legal[lang][app_key]
                ctx["doc"] = doc
            write(here + "index.html", env.get_template(template).render(**ctx))
            sitemap.append(alternates[lang])

    # Página raiz: escolhe o idioma (preferência salva ou idioma do navegador).
    write("index.html", env.get_template("root.html").render(
        site=site, strings=strings, langs=LANGS, default_lang=DEFAULT_LANG, domain=domain))

    # 404 (servida pelo GitHub Pages em qualquer caminho, por isso usa caminhos absolutos).
    write("404.html", env.get_template("404.html").render(
        site=site, strings=strings, langs=LANGS, year=year))

    write("CNAME", domain.split("://", 1)[1] + "\n")
    write(".nojekyll", "")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {domain}/sitemap.xml\n")
    urls = "\n".join(f"  <url><loc>{u}</loc></url>" for u in sitemap)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")

    print(f"Site gerado em {os.path.relpath(OUT, ROOT)}/ ({len(sitemap)} páginas + raiz e 404)")


def serve(port=8000):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=OUT)
    print(f"Servindo em http://localhost:{port}/ (Ctrl+C para parar)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
