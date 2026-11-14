
import json
import requests
from bs4 import BeautifulSoup

from fontes import listar_fontes


def contar_eventos(dados):
    """Procura dados estruturados do tipo Event."""

    total = 0

    if isinstance(dados, dict):
        tipo = dados.get("@type", [])

        if isinstance(tipo, str):
            tipo = [tipo]

        if any("Event" in item for item in tipo):
            total += 1

        for valor in dados.values():
            total += contar_eventos(valor)

    elif isinstance(dados, list):
        for item in dados:
            total += contar_eventos(item)

    return total


def testar_fonte(fonte):
    nome = fonte["nome"]
    url = fonte["url"]

    print("\n" + "=" * 50)
    print(f"FONTE: {nome}")
    print(f"URL: {url}")

    try:
        resposta = requests.get(
            url,
            headers={
                "User-Agent": "PortoABorra/1.0 (teste de acesso)"
            },
            timeout=20
        )

        print(f"Estado HTTP: {resposta.status_code}")
        print(f"Tipo de conteúdo: {resposta.headers.get('Content-Type', 'Não indicado')}")

        resposta.raise_for_status()

        sopa = BeautifulSoup(resposta.text, "html.parser")

        titulo = sopa.title.get_text(strip=True) if sopa.title else "Não identificado"
        print(f"Título da página: {titulo}")

        total_eventos = 0

        for script in sopa.find_all(
            "script",
            type="application/ld+json"
        ):
            try:
                dados = json.loads(script.string or script.get_text())
                total_eventos += contar_eventos(dados)
            except (json.JSONDecodeError, TypeError):
                continue

        print(f"Eventos identificados em dados estruturados: {total_eventos}")

    except requests.exceptions.RequestException as erro:
        print(f"Não foi possível aceder à página: {erro}")


if __name__ == "__main__":
    for fonte in listar_fontes():
        testar_fonte(fonte)

    print("\nTeste de acesso concluído.")
