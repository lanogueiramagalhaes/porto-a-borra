
import requests
from bs4 import BeautifulSoup

URL = "https://culturaja.pt/evento/o-fado-vai-ao-forum-b68107"

resposta = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=20
)

resposta.raise_for_status()
resposta.encoding = resposta.apparent_encoding

sopa = BeautifulSoup(resposta.text, "html.parser")

for campo in ["Quando", "Onde", "Preço"]:
    print("\n" + "=" * 50)
    print("CAMPO:", campo)

    elementos = sopa.find_all(
        string=lambda texto: texto and texto.strip() == campo
    )

    if not elementos:
        print("Não encontrado")
        continue

    for elemento in elementos[:3]:
        pai = elemento.parent

        print("\nHTML DO CAMPO:")
        print(pai.parent.prettify()[:2000])
