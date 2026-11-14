
import requests
from bs4 import BeautifulSoup

URL_AGENDA = "https://culturaja.pt/o-que-fazer/gratis"

URL_EVENTO = (
    "https://culturaja.pt/evento/"
    "o-fado-vai-ao-forum-b68107"
)

sessao = requests.Session()

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8"
}

sessao.headers.update(CABECALHOS)

print("1. A consultar a agenda...")

resposta_agenda = sessao.get(
    URL_AGENDA,
    timeout=20
)

print("Estado da agenda:", resposta_agenda.status_code)

if resposta_agenda.status_code != 200:
    print("Não foi possível consultar a agenda.")
    raise SystemExit(0)

print("\n2. A consultar a página do evento...")

sessao.headers.update({
    "Referer": URL_AGENDA
})

resposta_evento = sessao.get(
    URL_EVENTO,
    timeout=20
)

print("Estado do evento:", resposta_evento.status_code)

if resposta_evento.status_code == 200:
    resposta_evento.encoding = resposta_evento.apparent_encoding

    sopa = BeautifulSoup(
        resposta_evento.text,
        "html.parser"
    )

    print("\nTítulo da página:")
    print(sopa.title.get_text(strip=True) if sopa.title else "Não encontrado")

    print("\nTexto dos campos:")

    texto = sopa.get_text(" ", strip=True)

    for campo in ["Quando", "Onde", "Preço"]:
        posicao = texto.find(campo)

        if posicao >= 0:
            print(texto[posicao:posicao + 250])
        else:
            print(campo, "não encontrado")

elif resposta_evento.status_code == 403:
    print(
        "A CulturaJá recusou o acesso automático "
        "à página individual."
    )

else:
    print("Resposta inesperada:", resposta_evento.status_code)
