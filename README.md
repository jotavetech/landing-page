# Site da Jotave Tech

Site institucional da Jotave Tech em português e inglês, publicado pelo GitHub Pages em
**https://www.jotavetech.com**.

O design de referência é o arquivo [`telas landing-page.html`](telas%20landing-page.html)
(9 telas, versões para computador e celular). O site reproduz esse design: o CSS, o logotipo e
as ilustrações em pixels foram extraídos do próprio arquivo.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `content/site.json` | **Dados editáveis da empresa**: razão social, CNPJ, endereço, e-mail, telefone, WhatsApp, redes sociais, links das lojas, opções |
| `content/i18n/pt-br.json` | Todos os textos em português |
| `content/i18n/en.json` | Todos os textos em inglês (mesmas chaves do português; o build falha se faltar alguma) |
| `content/legal/pt-br.json` e `en.json` | Política de Privacidade e Termos de Uso de cada aplicativo (mesmas chaves nos dois idiomas) |
| `src/templates/` | Páginas (Jinja2), cabeçalho, rodapé e ilustrações SVG do design |
| `src/static/` | CSS, script, fontes (TeX Gyre Schola, usada pelo design) e imagens oficiais dos aplicativos |
| `build.py` | Gera o site em `_site/` |
| `.github/workflows/pages.yml` | Publica no GitHub Pages a cada push na branch `main` |

### Endereços

| Página | Português | Inglês |
| --- | --- | --- |
| Início | `/pt-br/` | `/en/` |
| Produtos | `/pt-br/produtos/` | `/en/products/` |
| GRO | `/pt-br/produtos/gro/` | `/en/products/gro/` |
| Balança Diária | `/pt-br/produtos/balanca-diaria/` | `/en/products/balanca-diaria/` |
| Spokn | `/pt-br/produtos/spokn/` | `/en/products/spokn/` |
| Soluções e possibilidades | `/pt-br/solucoes/` | `/en/solutions/` |
| Sobre | `/pt-br/sobre/` | `/en/about/` |
| Perguntas frequentes | `/pt-br/perguntas-frequentes/` | `/en/faq/` |
| Contato | `/pt-br/contato/` | `/en/contact/` |
| Política de Privacidade | `/pt-br/politica-de-privacidade/` | `/en/privacy-policy/` |
| Termos de Uso | `/pt-br/termos-de-uso/` | `/en/terms-of-use/` |
| Privacidade de um app | `/pt-br/produtos/<app>/politica-de-privacidade/` | `/en/products/<app>/privacy-policy/` |
| Termos de um app | `/pt-br/produtos/<app>/termos-de-uso/` | `/en/products/<app>/terms-of-use/` |

A raiz `/` envia o visitante ao idioma escolhido anteriormente ou, na primeira visita, ao idioma
do navegador (português → `/pt-br/`, demais → `/en/`). O seletor PT/EN fica no topo de todas as
páginas e no rodapé, leva à página equivalente no outro idioma e a escolha fica registrada.

## Como editar

- **Campos a preencher**: qualquer texto entre colchetes, como `[inserir CNPJ]`, aparece no site
  com destaque amarelo tracejado. Para preencher dados da empresa, edite `content/site.json`
  (campos vazios `""` mostram o marcador). Para textos, edite os arquivos de `content/i18n/`
  nos dois idiomas.
- **Missão, visão e valores**: em `pages.about` (`mission`, `vision`, `values`). Os textos atuais
  são as sugestões do design, marcadas no site como "Sugestão para aprovação".
- **Avisos "Para aprovação" / "Para preencher"**: aparecem enquanto
  `"show_editorial_notes": true` em `content/site.json`. Mude para `false` quando os textos
  forem aprovados.
- **Link da App Store**: preencha `apps.<app>.app_store` em `content/site.json`; o botão
  "Baixar na App Store" aparece automaticamente.
- **Formulário de contato**: o GitHub Pages não processa formulários. As mensagens vão pelo
  [FormSubmit](https://formsubmit.co) para o e-mail em `contact_form.action_url`
  (`https://formsubmit.co/ajax/<e-mail>`), sem sair da página. No primeiro envio, o FormSubmit
  manda um e-mail de ativação para esse endereço; clique no link para começar a receber.
  Sem `action_url`, o envio abre o programa de e-mail do visitante, endereçado a `company.email`.
- **Imagens dos aplicativos**: `src/static/img/apps/<app>/` (ícone e capturas de tela em WebP;
  `screen-1` aparece no topo da página do produto). Em `content/site.json`, `apps.<app>.screenshots`
  é a quantidade de imagens e `apps.<app>.gallery` diz quais aparecem em "Telas do aplicativo".
- **Políticas dos aplicativos**: o texto fica em `content/legal/`. As variáveis `{app}`, `{email}`,
  `{company}`, `{cnpj}`, `{address}` e `{brand}` são preenchidas no build; `{email}` vem de
  `apps.<app>.support_email` em `content/site.json`. Ao mudar um texto, atualize também a data
  `updated` do documento.

## Rodar localmente

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

```bash
.venv/bin/python build.py --serve
```

Abra http://localhost:8000/.

## Publicação no GitHub Pages (passos no painel do GitHub)

1. Faça push deste repositório para a branch `main` de `jotavetech/landing-page`.
2. Em **Settings → Pages → Build and deployment → Source**, escolha **GitHub Actions**.
   O workflow `Publicar no GitHub Pages` roda a cada push e publica `_site/`.
   (Em conta gratuita, o repositório precisa ser público para usar o Pages.)
3. Recomendado: verifique o domínio na organização, em
   **Organization settings → Pages → Add a domain** → `jotavetech.com`. O GitHub mostrará um
   registro TXT (`_github-pages-challenge-jotavetech`) para criar na Cloudflare.
4. Em **Settings → Pages → Custom domain**, informe `www.jotavetech.com` e salve.
   Com publicação via Actions, o domínio é definido aqui (o arquivo `CNAME` gerado é só referência).
5. Depois que a verificação de DNS passar, marque **Enforce HTTPS**.

## DNS na Cloudflare (configuração manual)

> **Não altere nem remova os registros de e-mail do Zoho** — MX, SPF (TXT `v=spf1 …`),
> DKIM (TXT `…._domainkey`) e DMARC (TXT `_dmarc`). Os registros abaixo são apenas de site e
> usam nomes diferentes. Antes de criar, confira se já existe um registro A/AAAA/CNAME para o
> mesmo nome (`@` ou `www`); se existir e for de um site antigo, substitua só esse registro.

### Zona `jotavetech.com` (domínio principal, servido pelo GitHub Pages)

| Tipo | Nome | Conteúdo | Proxy |
| --- | --- | --- | --- |
| CNAME | `www` | `jotavetech.github.io` | DNS only (nuvem cinza) |
| A | `@` | `185.199.108.153` | DNS only |
| A | `@` | `185.199.109.153` | DNS only |
| A | `@` | `185.199.110.153` | DNS only |
| A | `@` | `185.199.111.153` | DNS only |
| AAAA | `@` | `2606:50c0:8000::153` | DNS only |
| AAAA | `@` | `2606:50c0:8001::153` | DNS only |
| AAAA | `@` | `2606:50c0:8002::153` | DNS only |
| AAAA | `@` | `2606:50c0:8003::153` | DNS only |
| TXT | `_github-pages-challenge-jotavetech` | valor exibido pelo GitHub no passo 3 | — |

Com esses registros, `jotavetech.com` (sem www) é redirecionado pelo próprio GitHub para
`https://www.jotavetech.com`. Mantenha "DNS only" para que o GitHub emita o certificado HTTPS.

### Zona `jotavetech.com.br` (redireciona para a versão em português)

O GitHub Pages aceita um único domínio personalizado por site, então o `.com.br` é
redirecionado pela Cloudflare:

1. Registros (somente se ainda não existirem registros de site para esses nomes):

   | Tipo | Nome | Conteúdo | Proxy |
   | --- | --- | --- | --- |
   | A | `@` | `192.0.2.1` | Proxied (nuvem laranja) |
   | CNAME | `www` | `jotavetech.com.br` | Proxied |

   O IP `192.0.2.1` é um endereço reservado: o tráfego nunca chega a ele, porque a Cloudflare
   responde com o redirecionamento.
2. **Rules → Redirect Rules → Create rule**:
   - Quando: *Hostname* é igual a `jotavetech.com.br` **ou** *Hostname* é igual a
     `www.jotavetech.com.br`
   - Então: *Static redirect* para `https://www.jotavetech.com/pt-br/`, código **301**.
3. Em **SSL/TLS**, mantenha o modo padrão; o certificado universal da Cloudflare cobre o
   `.com.br` e o `www`.

Depois do redirecionamento, **o navegador exibirá o endereço `www.jotavetech.com/pt-br/`**
(e não `.com.br`) — esse é o comportamento esperado.
