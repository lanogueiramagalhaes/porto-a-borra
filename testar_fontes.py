
import requests
from bs4 import BeautifulSoup

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

print("A consultar a agenda...")
agenda = sessao.get(URL_AGENDA, timeout=20)
agenda.raise_for_status()

print("A consultar o evento...")
evento = sessao.get(
    URL_EVENTO,
    headers={"Referer": URL_AGENDA},
    timeout=20
)
evento.raise_for_status()
evento.encoding = evento.apparent_encoding

sopa = BeautifulSoup(evento.text, "html.parser")

for campo in ["Quando", "Onde", "Preço"]:
    print("\n" + "=" * 60)
    print("CAMPO:", campo)

    elementos = sopa.find_all(
        string=lambda texto: texto and texto.strip() == campo
    )

    if not elementos:
        print("Campo não encontrado")
        continue

    for elemento in elementos[:2]:
        print("\nESTRUTURA HTML:")

        pai = elemento.parent

        if pai.parent:
            print(pai.parent.prettify()[:3000])
        else:
            print(pai.prettify()[:3000])
