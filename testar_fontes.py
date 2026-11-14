
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

URL_AGENDA = "https://culturaja.pt/o-que-fazer/gratis"

URL_EVENTO = (
    "https://culturaja.pt/evento/"
    "o-fado-vai-ao-forum-b68107"
)

sessao = requests.Session()

sessao.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8"
})


# --------------------------------------------------
# CONSULTAR PÁGINAS
# --------------------------------------------------

def obter_pagina(url, referer=None):
    cabecalhos = {}

    if referer:
        cabecalhos["Referer"] = referer

    resposta = sessao.get(
        url,
        headers=cabecalhos,
        timeout=20
    )

    resposta.raise_for_status()
    resposta.encoding = resposta.apparent_encoding

    return BeautifulSoup(resposta.text, "html.parser")


# --------------------------------------------------
# IDENTIFICAR CAMPOS
# --------------------------------------------------

def obter_campo(sopa, nome):
    for dt in sopa.find_all("dt"):
        if dt.get_text(" ", strip=True) == nome:
            return dt.find_next_sibling("dd")

    return None


# --------------------------------------------------
# EXTRAIR INFORMAÇÃO DO EVENTO
# --------------------------------------------------

def extrair_evento(url):

    sopa = obter_pagina(url, URL_AGENDA)

    campo_quando = obter_campo(sopa, "Quando")
    campo_onde = obter_campo(sopa, "Onde")
    campo_preco = obter_campo(sopa, "Preço")
    campo_publico = obter_campo(sopa, "Para quem")

    # TÍTULO
    titulo = ""

    elemento_titulo = sopa.find("h1")

    if elemento_titulo:
        titulo = elemento_titulo.get_text(" ", strip=True)

    # DATA E HORÁRIO
    quando = ""
    horario = ""

    if campo_quando:
        quando = campo_quando.get_text(" ", strip=True)

        elemento_horario = campo_quando.find("span")

        if elemento_horario:
            horario = elemento_horario.get_text(
                " ", strip=True
            )

    # LOCAL E MUNICÍPIO
    local = ""
    municipio = ""

    if campo_onde:
        elemento_local = campo_onde.find("a")
        elemento_municipio = campo_onde.find("span")

        if elemento_local:
            local = elemento_local.get_text(
                " ", strip=True
            )
        else:
            local = campo_onde.get_text(
                " ", strip=True
            )

        if elemento_municipio:
            municipio = elemento_municipio.get_text(
                " ", strip=True
            )

    # PREÇO
    preco = ""
    detalhe_preco = ""

    if campo_preco:
        preco = campo_preco.get_text(
            " ", strip=True
        )

        elemento_detalhe = campo_preco.find("span")

        if elemento_detalhe:
            detalhe_preco = elemento_detalhe.get_text(
                " ", strip=True
            )

    # PÚBLICO
    publico = ""

    if campo_publico:
        publico = campo_publico.get_text(
            " ", strip=True
        )

    # FONTE OFICIAL
    fonte_oficial = ""

    for link in sopa.find_all("a", href=True):
        texto_link = link.get_text(
            " ", strip=True
        ).lower()

        if "fonte oficial" in texto_link:
            fonte_oficial = urljoin(
                url,
                link["href"]
            )
            break

    # RESULTADO
    return {
        "titulo": titulo,
        "quando": quando,
        "horario": horario,
        "local": local,
        "municipio": municipio,
        "preco": preco,
        "detalhe_preco": detalhe_preco,
        "publico": publico,
        "url_evento": url,
        "fonte_oficial": fonte_oficial
    }


# --------------------------------------------------
# EXECUTAR TESTE
# --------------------------------------------------

if __name__ == "__main__":

    print("A consultar a agenda...")

    agenda = obter_pagina(URL_AGENDA)

    print("Agenda consultada com sucesso.")

    print("\nA extrair informação do evento...")

    evento = extrair_evento(URL_EVENTO)

    print("\nPORTO À BORLA - TESTE DE EXTRAÇÃO")
    print("=" * 55)

    for campo, valor in evento.items():
        print(f"{campo.upper()}: {valor}")

    print("\n" + "=" * 55)
    print("TESTE CONCLUÍDO.")

