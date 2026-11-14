
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://culturaja.pt/o-que-fazer/gratis"

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
    print("=" * 60)
    print("CULTURAJÁ - EVENTOS GRATUITOS")

    sopa = obter_pagina(URL)

    cartoes = sopa.select("article.cartao")

    print("Cartões encontrados:", len(cartoes))

    for numero, cartao in enumerate(cartoes[:10], start=1):
        link = cartao.find("a", href=True)

        if not link:
            continue

        titulo = link.get_text(" ", strip=True)
        url_evento = urljoin(URL, link["href"])

        concelho = cartao.select_one(".concelho")
        categoria = cartao.select_one(".categoria")

        print("\n" + "-" * 50)
        print("EVENTO:", numero)
        print("TÍTULO:", titulo)
        print("CONCELHO:", concelho.get_text(strip=True) if concelho else "Não identificado")
        print("CATEGORIA:", categoria.get_text(strip=True) if categoria else "Não identificada")
        print("URL:", url_evento)

        try:
            pagina_evento = obter_pagina(url_evento)
            texto = pagina_evento.get_text(" ", strip=True)

            if "Preço" in texto:
                parte_preco = texto.split("Preço", 1)[1][:180]
                print("INFORMAÇÃO DE PREÇO:", parte_preco)
            else:
                print("INFORMAÇÃO DE PREÇO: Não encontrada")

            fontes = [
                a.get("href")
                for a in pagina_evento.find_all("a", href=True)
                if "fonte oficial" in a.get_text(" ", strip=True).lower()
            ]

            print("FONTE OFICIAL:", fontes[0] if fontes else "Não identificada")

        except Exception as erro:
            print("Erro ao consultar evento:", erro)


if __name__ == "__main__":
    analisar()
