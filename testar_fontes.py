
import requests
from bs4 import BeautifulSoup
from fontes import listar_fontes


def testar_fonte(fonte):
    nome = fonte["nome"]
    url = fonte["url"]

    print("\n" + "=" * 60)
    print(f"FONTE: {nome}")
    print(f"URL: {url}")

    try:
        resposta = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 PortoABorra/1.0"
            },
            timeout=20
        )

        print(f"Estado HTTP: {resposta.status_code}")

        resposta.raise_for_status()

        # Corrigir a interpretação dos caracteres
        resposta.encoding = resposta.apparent_encoding

        sopa = BeautifulSoup(resposta.text, "html.parser")

        titulo = sopa.title.get_text(strip=True) if sopa.title else "Não identificado"

        print(f"\nTÍTULO: {titulo}")

        print("\nTÍTULOS ENCONTRADOS:")

        for elemento in sopa.find_all(["h1", "h2", "h3"])[:20]:
            texto = elemento.get_text(" ", strip=True)

            if texto:
                print("-", texto)

        print("\nTEXTO DA PÁGINA:")

        texto_pagina = sopa.get_text(" ", strip=True)
        print(texto_pagina[:2500])

        print("\nPRIMEIROS LINKS ENCONTRADOS:")

        total = 0

        for link in sopa.find_all("a", href=True):
            texto = link.get_text(" ", strip=True)
            endereco = link["href"]

            if texto and len(texto) > 2:
                print(f"- {texto[:100]} | {endereco}")
                total += 1

            if total >= 25:
                break

        print(f"\nTotal de links apresentados: {total}")

    except requests.exceptions.RequestException as erro:
        print(f"Erro de acesso: {erro}")


if __name__ == "__main__":
    for fonte in listar_fontes():
        testar_fonte(fonte)

    print("\nAnálise das páginas concluída.")
