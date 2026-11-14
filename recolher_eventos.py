
import json
import re
import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin


# PORTO À BORLA
# Recolha automática de eventos gratuitos da CulturaJá


URL_AGENDA = "https://culturaja.pt/o-que-fazer/gratis"

MUNICIPIOS = [
    "Amarante",
    "Baião",
    "Felgueiras",
    "Gondomar",
    "Lousada",
    "Maia",
    "Marco de Canaveses",
    "Matosinhos",
    "Paços de Ferreira",
    "Paredes",
    "Penafiel",
    "Porto",
    "Póvoa de Varzim",
    "Santo Tirso",
    "Trofa",
    "Valongo",
    "Vila do Conde",
    "Vila Nova de Gaia"
]

# Expressões que podem indicar que a gratuitidade
# está sujeita a condições especiais.
TERMOS_CONDICIONAIS = [
    "associados",
    "sócios",
    "socios",
    "mediante apresentação",
    "mediante comprovativo",
    "exclusivo para",
    "apenas para",
    "reservado a",
    "reservada a",
    "cartão de estudante",
    "cartao de estudante"
]

sessao = requests.Session()

sessao.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8"
})


def obter_pagina(url, referer=None):
    """Consulta uma página e devolve o seu conteúdo HTML."""

    cabecalhos = {}

    if referer:
        cabecalhos["Referer"] = referer

    resposta = sessao.get(
        url,
        headers=cabecalhos,
        timeout=30
    )

    resposta.raise_for_status()
    resposta.encoding = resposta.apparent_encoding

    return BeautifulSoup(resposta.text, "html.parser")


def obter_campo(sopa, nome):
    """Obtém o conteúdo associado a um campo dt/dd."""

    for dt in sopa.find_all("dt"):
        if dt.get_text(" ", strip=True) == nome:
            return dt.find_next_sibling("dd")

    return None


def obter_texto(elemento):
    """Devolve texto limpo de um elemento HTML."""

    if elemento:
        return elemento.get_text(" ", strip=True)

    return ""


def gratuitidade_confirmada(campo_preco, detalhe_preco):
    """
    Só aceita eventos identificados como gratuitos
    e sem condições especiais detetadas no texto.
    """

    if campo_preco is None:
        return False

    classes = campo_preco.get("class", [])

    if "gratis" not in classes:
        return False

    texto = detalhe_preco.lower()

    for termo in TERMOS_CONDICIONAIS:
        if termo in texto:
            return False

    # Tem de existir uma indicação explícita de gratuitidade.
    indicacoes_gratuitas = [
        "gratuito",
        "gratuita",
        "grátis",
        "gratis",
        "entrada livre",
        "entrada gratuita"
    ]

    return any(
        indicacao in texto
        for indicacao in indicacoes_gratuitas
    )


def obter_datas_do_cartao(cartao):
    """
    Tenta obter as datas estruturadas no cartão do evento.
    Se não estiverem disponíveis, devolve campos vazios.
    """

    inicio = ""
    fim = ""

    elemento = cartao.find(
        attrs={
            "data-inicio": True
        }
    )

    if elemento:
        inicio = elemento.get("data-inicio", "")

    elemento = cartao.find(
        attrs={
            "data-fim": True
        }
    )

    if elemento:
        fim = elemento.get("data-fim", "")

    return inicio, fim


def extrair_evento(url_evento, municipio_cartao, categoria_cartao,
                   data_inicio, data_fim):
    """Consulta a página individual e extrai os dados do evento."""

    sopa = obter_pagina(url_evento, URL_AGENDA)

    titulo = obter_texto(sopa.find("h1"))

    campo_quando = obter_campo(sopa, "Quando")
    campo_onde = obter_campo(sopa, "Onde")
    campo_preco = obter_campo(sopa, "Preço")
    campo_publico = obter_campo(sopa, "Para quem")

    quando = obter_texto(campo_quando)
    local = ""
    municipio = municipio_cartao

    if campo_onde:
        elemento_local = campo_onde.find("a")
        elemento_municipio = campo_onde.find("span")

        if elemento_local:
            local = obter_texto(elemento_local)
        else:
            local = obter_texto(campo_onde)

        if elemento_municipio:
            municipio = obter_texto(elemento_municipio)

    preco = obter_texto(campo_preco)

    detalhe_preco = ""

    if campo_preco:
        detalhe = campo_preco.find("span")

        if detalhe:
            detalhe_preco = obter_texto(detalhe)

    publico = obter_texto(campo_publico)

    fonte_oficial = ""

    for link in sopa.find_all("a", href=True):
        texto_link = obter_texto(link).lower()

        if "fonte oficial" in texto_link:
            fonte_oficial = urljoin(
                url_evento,
                link["href"]
            )
            break

    # Confirma se o município pertence à lista pretendida.
    if municipio not in MUNICIPIOS:
        return None

    # Confirma se o preço é efetivamente gratuito.
    if not gratuitidade_confirmada(
        campo_preco,
        detalhe_preco
    ):
        return None

    # Não publica eventos sem título ou local confirmado.
    if not titulo or not local:
        return None

    if "a confirmar" in local.lower():
        return None

    return {
        "titulo": titulo,
        "municipio": municipio,
        "categoria": categoria_cartao,
        "quando": quando,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "horario": "",
        "local": local,
        "preco": preco,
        "detalhe_preco": detalhe_preco,
        "publico": publico,
        "url_evento": url_evento,
        "fonte_oficial": fonte_oficial
    }


def recolher_eventos():
    """Recolhe os eventos gratuitos disponíveis na agenda."""

    print("A consultar a agenda da CulturaJá...")

    sopa = obter_pagina(URL_AGENDA)

    cartoes = sopa.find_all("article", class_="cartao")

    print(f"Cartões encontrados: {len(cartoes)}")

    eventos = []
    urls_processados = set()

    for cartao in cartoes:

        # Município
        municipio_elemento = cartao.find(
            class_="concelho"
        )

        municipio = obter_texto(municipio_elemento)

        if municipio not in MUNICIPIOS:
            continue

        # Categoria
        categoria_elemento = cartao.find(
            class_="categoria"
        )

        categoria = obter_texto(categoria_elemento)

        # Ligação individual do evento
        link_evento = cartao.find(
            "a",
            href=re.compile(r"/evento/")
        )

        if not link_evento:
            continue

        url_evento = urljoin(
            URL_AGENDA,
            link_evento["href"]
        )

        if url_evento in urls_processados:
            continue

        urls_processados.add(url_evento)

        data_inicio, data_fim = obter_datas_do_cartao(cartao)

        print(f"A analisar: {obter_texto(link_evento)}")

        try:
            evento = extrair_evento(
                url_evento,
                municipio,
                categoria,
                data_inicio,
                data_fim
            )

            if evento:
                eventos.append(evento)
                print("  -> Evento aceite.")
            else:
                print("  -> Evento excluído na validação.")

        except requests.RequestException as erro:
            print(f"  -> Erro de acesso: {erro}")

        except Exception as erro:
            print(f"  -> Erro na leitura: {erro}")

        # Pequena pausa para não sobrecarregar a fonte.
        time.sleep(0.5)

    return eventos


if __name__ == "__main__":

    eventos = recolher_eventos()

    # Guarda os eventos num ficheiro JSON.
    with open(
        "eventos.json",
        "w",
        encoding="utf-8"
    ) as ficheiro:

        json.dump(
            eventos,
            ficheiro,
            ensure_ascii=False,
            indent=4
        )

    print("\n" + "=" * 55)
    print("RECOLHA CONCLUÍDA")
    print("=" * 55)

    print(f"Eventos aceites: {len(eventos)}")
    print("Ficheiro criado: eventos.json")
