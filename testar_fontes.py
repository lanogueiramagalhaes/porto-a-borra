
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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


def analisar_eventos(nome_fonte, url, seletor, limite=3):
    print("\n" + "=" * 60)
    print(nome_fonte)

    sopa = obter_pagina(url)
    cartoes = sopa.select(seletor)

    print("Cartões encontrados:", len(cartoes))

    links_eventos = []

    for cartao in cartoes:
        link = cartao.find("a", href=True)

        if link:
            endereco = urljoin(url, link["href"])

            if endereco not in links_eventos:
                links_eventos.append(endereco)

    for numero, endereco in enumerate(links_eventos[:limite], start=1):
        print("\n" + "-" * 60)
        print("EVENTO", numero)
        print("URL:", endereco)

        try:
            pagina = obter_pagina(endereco)

            titulo = (
                pagina.title.get_text(strip=True)
                if pagina.title else "Não identificado"
            )

            print("TÍTULO DA PÁGINA:", titulo)

            texto = pagina.get_text(" ", strip=True)

            print("\nTEXTO DA PÁGINA:")
            print(texto[:4500])

            print("\nLIGAÇÕES ENCONTRADAS:")

            for link in pagina.find_all("a", href=True):
                texto_link = link.get_text(" ", strip=True)
                url_link = urljoin(endereco, link["href"])

                if texto_link:
                    print("-", texto_link[:100], "|", url_link)

        except Exception as erro:
            print("Erro ao analisar o evento:", erro)


if __name__ == "__main__":

    analisar_eventos(
        "CULTURAJÁ",
        "https://culturaja.pt/agenda/",
        "article.cartao",
        limite=3
    )

    analisar_eventos(
        "AGENDA PORTO",
        "https://www.agenda-porto.pt/",
        "div[data-bl-name='Card. Card Event']",
        limite=3
    )

    print("\nAnálise das páginas individuais concluída.")
