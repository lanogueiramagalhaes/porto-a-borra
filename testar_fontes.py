
import requests
from bs4 import BeautifulSoup


def obter_pagina(url):
    resposta = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 PortoABorra/1.0"},
        timeout=20
    )
    resposta.raise_for_status()
    resposta.encoding = resposta.apparent_encoding

    return BeautifulSoup(resposta.text, "html.parser")


def testar_culturaja():
    print("\n" + "=" * 60)
    print("CULTURAJÁ - ANÁLISE DOS CARTÕES")

    sopa = obter_pagina("https://culturaja.pt/agenda/")

    cartoes = sopa.select("article.cartao")

    print("Cartões encontrados:", len(cartoes))

    for numero, cartao in enumerate(cartoes[:2], start=1):
        print(f"\n--- CARTÃO {numero} ---")

        print("TEXTO COMPLETO:")
        print(cartao.get_text(" ", strip=True))

        print("\nATRIBUTOS DOS ELEMENTOS:")
        for elemento in cartao.find_all(["a", "button", "span"]):
            if elemento.name == "button":
                print("BUTTON:", elemento.attrs)

            elif elemento.name == "a":
                print("LINK:", elemento.get_text(" ", strip=True))
                print("URL:", elemento.get("href"))

            elif elemento.get("class"):
                print(
                    "SPAN:",
                    elemento.get("class"),
                    elemento.get_text(" ", strip=True)
                )

        print("\nHTML COMPLETO DO CARTÃO:")
        print(cartao.prettify()[:7000])


def testar_agenda_porto():
    print("\n" + "=" * 60)
    print("AGENDA PORTO - ANÁLISE DOS LINKS")

    sopa = obter_pagina("https://www.agenda-porto.pt/")

    links = sopa.find_all("a", href=True)

    encontrados = 0

    for link in links:
        url = link.get("href", "")

        if any(
            palavra in url.lower()
            for palavra in ["evento", "ciclo", "atividade"]
        ):
            print("\nTÍTULO:", link.get_text(" ", strip=True))
            print("URL:", url)

            pai = link.parent

            if pai:
                print("HTML DO ELEMENTO:")
                print(pai.prettify()[:2500])

            encontrados += 1

            if encontrados >= 5:
                break

    print("\nLinks de eventos analisados:", encontrados)


if __name__ == "__main__":
    try:
        testar_culturaja()
    except Exception as erro:
        print("Erro no CulturaJá:", erro)

    try:
        testar_agenda_porto()
    except Exception as erro:
        print("Erro na Agenda Porto:", erro)

    print("\nAnálise concluída.")
