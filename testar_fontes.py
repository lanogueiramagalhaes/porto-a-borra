
import requests
from bs4 import BeautifulSoup
from fontes import listar_fontes


def inspecionar_fonte(fonte):
    print("\n" + "=" * 60)
    print("FONTE:", fonte["nome"])

    resposta = requests.get(
        fonte["url"],
        headers={"User-Agent": "Mozilla/5.0 PortoABorra/1.0"},
        timeout=20
    )

    resposta.raise_for_status()
    resposta.encoding = resposta.apparent_encoding

    sopa = BeautifulSoup(resposta.text, "html.parser")

    titulos = sopa.find_all(["h2", "h3", "h4"])

    print("\nESTRUTURA DOS EVENTOS:")

    encontrados = 0

    for titulo in titulos:
        nome = titulo.get_text(" ", strip=True)

        if not nome or len(nome) < 4:
            continue

        elemento = titulo

        # Sobe na estrutura HTML para encontrar o cartão
        for _ in range(3):
            if elemento.parent:
                elemento = elemento.parent

        print("\nTÍTULO:", nome)
        print("HTML DO CARTÃO:")
        print(elemento.prettify()[:1800])

        encontrados += 1

        if encontrados >= 5:
            break

    print("\nTotal de cartões inspecionados:", encontrados)


if __name__ == "__main__":
    for fonte in listar_fontes():
        try:
            inspecionar_fonte(fonte)
        except Exception as erro:
            print("Erro:", erro)
