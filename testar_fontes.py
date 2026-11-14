
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://culturaja.pt/o-que-fazer/gratis"

MUNICIPIOS = [
    "Amarante", "Baião", "Felgueiras", "Gondomar",
    "Lousada", "Maia", "Marco de Canaveses",
    "Matosinhos", "Paços de Ferreira", "Paredes",
    "Penafiel", "Porto", "Póvoa de Varzim",
    "Santo Tirso", "Trofa", "Valongo",
    "Vila do Conde", "Vila Nova de Gaia"
]

CABECALHOS = {
    "User-Agent": "Mozilla/5.0 PortoABorra/1.0"
}


def obter_pagina(url):
    resposta = requests.get(
        url,
        headers=CABECALHOS,
        timeout=20
    )
    resposta.raise_for_status()
    resposta.encoding = resposta.apparent_encoding
    return BeautifulSoup(resposta.text, "html.parser")


def analisar():
    sopa = obter_pagina(URL)
    cartoes = sopa.select("article.cartao")

    print("TOTAL DE CARTÕES:", len(cartoes))

    analisados = 0

    for cartao in cartoes:
        link = cartao.select_one("h3 a[href]")

        if not link:
            link = cartao.find("a", href=True)

        if not link:
            continue

        titulo = link.get_text(" ", strip=True)
        url_evento = urljoin(URL, link["href"])

        concelho_elemento = cartao.select_one(".concelho")
        categoria_elemento = cartao.select_one(".categoria")

        concelho = (
            concelho_elemento.get_text(" ", strip=True)
            if concelho_elemento else "Não identificado"
        )

        categoria = (
            categoria_elemento.get_text(" ", strip=True)
            if categoria_elemento else "Não identificada"
        )

        if concelho not in MUNICIPIOS:
            continue

        try:
            pagina = obter_pagina(url_evento)
            texto = pagina.get_text(" ", strip=True)

            print("\n" + "=" * 60)
            print("EVENTO:", titulo)
            print("MUNICÍPIO:", concelho)
            print("CATEGORIA:", categoria)
            print("URL:", url_evento)

            for campo in ["Quando", "Onde", "Preço"]:
                posicao = texto.find(campo)

                if posicao >= 0:
                    print(
                        campo.upper() + ":",
                        texto[posicao:posicao + 300]
                    )
                else:
                    print(campo.upper() + ": Não identificado")

            fontes = [
                a.get("href")
                for a in pagina.find_all("a", href=True)
                if "fonte oficial" in a.get_text(" ", strip=True).lower()
            ]

            print(
                "FONTE OFICIAL:",
                fontes[0] if fontes else "Não identificada"
            )

            analisados += 1

            if analisados >= 10:
                break

        except Exception as erro:
            print("ERRO:", erro)


if __name__ == "__main__":
    analisar()
