
import json
import re
import time
import calendar
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from zoneinfo import ZoneInfo


# =========================================================
# CONFIGURAÇÕES
# =========================================================

URL_AGENDA = "https://culturaja.pt/agenda/?preco=gratuito"
FUSO_HORARIO = ZoneInfo("Europe/Lisbon")

MUNICIPIOS = [
    "Amarante", "Baião", "Felgueiras", "Gondomar", "Lousada",
    "Maia", "Marco de Canaveses", "Matosinhos", "Paços de Ferreira",
    "Paredes", "Penafiel", "Porto", "Póvoa de Varzim",
    "Santo Tirso", "Trofa", "Valongo", "Vila do Conde",
    "Vila Nova de Gaia"
]

CATEGORIAS_VALIDAS = [
    "Música", "Exposições", "Teatro", "Cinema", "Workshops",
    "Desporto", "Feiras e mercados", "Ar livre", "Conferências",
    "Livros e ideias", "Natureza e ar livre", "Teatro e dança",
    "Feiras e gastronomia", "Outros"
]


# =========================================================
# LIGAÇÃO À FONTE
# =========================================================

sessao = requests.Session()

sessao.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8"
})


def obter_pagina(url, referer=None):
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


def obter_texto(elemento):
    if elemento:
        return elemento.get_text(" ", strip=True)

    return ""


def obter_campo(sopa, nome):
    for dt in sopa.find_all("dt"):
        if obter_texto(dt) == nome:
            return dt.find_next_sibling("dd")

    return None


# =========================================================
# PERÍODO DE RECOLHA: HOJE ATÉ DOIS MESES DEPOIS
# =========================================================

def adicionar_meses(data_original, meses):
    mes_total = data_original.month - 1 + meses

    ano = data_original.year + mes_total // 12
    mes = mes_total % 12 + 1

    dia = min(
        data_original.day,
        calendar.monthrange(ano, mes)[1]
    )

    return data_original.replace(
        year=ano,
        month=mes,
        day=dia
    )


def obter_periodo_recolha():
    hoje = datetime.now(FUSO_HORARIO).date()
    fim_periodo = adicionar_meses(hoje, 2)

    return hoje, fim_periodo


def converter_data(data_texto):
    if not data_texto:
        return None

    try:
        data = datetime.fromisoformat(
            data_texto.replace("Z", "+00:00")
        )

        if data.tzinfo is None:
            data = data.replace(tzinfo=FUSO_HORARIO)
        else:
            data = data.astimezone(FUSO_HORARIO)

        return data.date()

    except (ValueError, TypeError):
        return None


def evento_no_periodo(
    data_inicio,
    data_fim,
    inicio_periodo,
    fim_periodo
):
    inicio = converter_data(data_inicio)
    fim = converter_data(data_fim)

    if not inicio or not fim:
        return False

    return (
        inicio <= fim_periodo
        and fim >= inicio_periodo
    )


def obter_datas_do_cartao(cartao):
    inicio = ""
    fim = ""

    elemento_inicio = cartao.find(attrs={"data-inicio": True})
    elemento_fim = cartao.find(attrs={"data-fim": True})

    if elemento_inicio:
        inicio = elemento_inicio.get("data-inicio", "")

    if elemento_fim:
        fim = elemento_fim.get("data-fim", "")

    return inicio, fim


# =========================================================
# EXTRAÇÃO DOS HORÁRIOS
# =========================================================

def extrair_horarios(campo_quando):
    texto = obter_texto(campo_quando)

    horarios = re.findall(
        r"(?<!\d)\d{1,2}(?::\d{2}|h\d{0,2})(?!\d)",
        texto,
        flags=re.IGNORECASE
    )

    horarios_unicos = list(dict.fromkeys(horarios))

    return " / ".join(horarios_unicos)


# =========================================================
# EXTRAÇÃO DO LOCAL E MUNICÍPIO
# =========================================================

def extrair_local_e_municipio(campo_onde, municipio_cartao):
    local = ""
    municipio = municipio_cartao

    if not campo_onde:
        return local, municipio

    elemento_local = campo_onde.find("a")
    elemento_municipio = campo_onde.find("span")

    if elemento_local:
        local = obter_texto(elemento_local)
    else:
        local = obter_texto(campo_onde)

    if elemento_municipio:
        municipio = obter_texto(elemento_municipio)

    if municipio:
        local = re.sub(
            r"\s+" + re.escape(municipio) + r"$",
            "",
            local,
            flags=re.IGNORECASE
        ).strip()

    if local.lower().endswith(
        (" da", " de", " do", " das", " dos", " à", " ao")
    ):
        local = f"{local} {municipio}".strip()

    return local, municipio


# =========================================================
# VALIDAÇÃO DA GRATUITIDADE
# =========================================================

def validar_gratuitidade(campo_preco):

    if campo_preco is None:
        return False, "Preço não identificado"

    texto = obter_texto(campo_preco).lower()

    indicacoes_gratuitas = [
        "gratuito",
        "gratuita",
        "grátis",
        "gratis",
        "entrada livre",
        "entrada gratuita"
    ]

    termos_condicionais = [
        "associados",
        "sócios",
        "socios",
        "mediante apresentação",
        "mediante comprovativo",
        "exclusivo para",
        "exclusiva para",
        "apenas para",
        "reservado a",
        "reservada a",
        "cartão de estudante",
        "cartao de estudante",
        "gratuito para estudantes",
        "gratuita para estudantes",
        "gratuito para professores",
        "gratuita para professores",
        "apenas na inauguração",
        "na inauguração",
        "inauguração gratuita"
    ]

    termos_nao_gratuitos = [
        "preço a confirmar",
        "preco a confirmar",
        "sob consulta",
        "bilhete pago",
        "bilhetes pagos",
        "entrada paga",
        "pago"
    ]

    # Rejeitar preços pagos ou ainda por confirmar
    if any(
        termo in texto
        for termo in termos_nao_gratuitos
    ):
        return False, "Preço pago ou por confirmar"

    # Rejeitar gratuitidade sujeita a condições
    if any(
        termo in texto
        for termo in termos_condicionais
    ):
        return False, "Gratuitidade sujeita a condições especiais"

    # Exigir indicação explícita de gratuitidade
    gratuito = any(
        indicacao in texto
        for indicacao in indicacoes_gratuitas
    )

    if not gratuito:
        return False, "Gratuitidade não confirmada no texto do preço"

    return True, ""


# =========================================================
# CATEGORIAS
# =========================================================

def normalizar_categoria(categoria):
    if not categoria:
        return "Outros"

    if categoria in CATEGORIAS_VALIDAS:
        return categoria

    return "Outros"


# =========================================================
# FONTE OFICIAL
# =========================================================

def obter_fonte_oficial(sopa, url_evento):
    for link in sopa.find_all("a", href=True):
        texto_link = obter_texto(link).lower()

        if "fonte oficial" in texto_link:
            return urljoin(url_evento, link["href"])

    return ""


# =========================================================
# EXTRAÇÃO E VALIDAÇÃO DE CADA EVENTO
# =========================================================

def extrair_evento(
    url_evento,
    municipio_cartao,
    categoria_cartao,
    data_inicio,
    data_fim
):

    sopa = obter_pagina(url_evento, URL_AGENDA)

    titulo = obter_texto(sopa.find("h1"))

    campo_quando = obter_campo(sopa, "Quando")
    campo_onde = obter_campo(sopa, "Onde")
    campo_preco = obter_campo(sopa, "Preço")
    campo_publico = obter_campo(sopa, "Para quem")

    quando = obter_texto(campo_quando)
    horario = extrair_horarios(campo_quando)

    local, municipio = extrair_local_e_municipio(
        campo_onde,
        municipio_cartao
    )

    preco = obter_texto(campo_preco)

    detalhe_preco = ""

    if campo_preco:
        detalhe_preco = obter_texto(
            campo_preco.find("span")
        )

    publico = obter_texto(campo_publico)

    # -----------------------------------------------------
    # DIAGNÓSTICO DETALHADO DO PREÇO
    # -----------------------------------------------------

    print("     --- DIAGNÓSTICO DO PREÇO ---")

    print(
        f"     TEXTO DO PREÇO: {preco!r}"
    )

    print(
        f"     CLASSES DO PREÇO: "
        f"{campo_preco.get('class', []) if campo_preco else 'Campo inexistente'}"
    )

    print(
        f"     DETALHE DO PREÇO: {detalhe_preco!r}"
    )

    print(
        f"     HTML ORIGINAL DO PREÇO: "
        f"{str(campo_preco)[:1500] if campo_preco else 'Campo inexistente'}"
    )

    print("     ---------------------------")

    fonte_oficial = obter_fonte_oficial(
        sopa,
        url_evento
    )

    categoria = normalizar_categoria(categoria_cartao)

    # Validar município
    if municipio not in MUNICIPIOS:
        return None, "Município fora dos 18 municípios abrangidos"

    # Validar gratuitidade
    gratuito, motivo_preco = validar_gratuitidade(campo_preco)

    if not gratuito:
        return None, motivo_preco

    # Validar título
    if not titulo:
        return None, "Título do evento em falta"

    # Validar local
    if not local:
        return None, "Local do evento em falta"

    if "a confirmar" in local.lower():
        return None, "Local ainda por confirmar"

    # Validar fonte oficial
    if not fonte_oficial:
        return None, "Ligação à fonte oficial não identificada"

    evento = {
        "titulo": titulo,
        "municipio": municipio,
        "categoria": categoria,
        "quando": quando,
        "horario": horario,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "local": local,
        "preco": preco,
        "detalhe_preco": detalhe_preco,
        "publico": publico,
        "url_evento": url_evento,
        "fonte_oficial": fonte_oficial
    }

    return evento, ""


# =========================================================
# RECOLHA DE TODOS OS EVENTOS
# =========================================================

def recolher_eventos():

    inicio_periodo, fim_periodo = obter_periodo_recolha()

    print("=" * 55)
    print("PORTO À BORLA - RECOLHA DE EVENTOS")
    print("=" * 55)

    print(
        f"Período: {inicio_periodo.strftime('%d/%m/%Y')} "
        f"a {fim_periodo.strftime('%d/%m/%Y')}"
    )

    print("\nA consultar a agenda da CulturaJá...")

    sopa = obter_pagina(URL_AGENDA)

    cartoes = sopa.find_all(
        "article",
        class_="cartao"
    )

    print(f"Cartões encontrados: {len(cartoes)}")

    eventos = []
    urls_processados = set()

    motivos_exclusao = {}

    excluidos_periodo = 0
    excluidos_municipio = 0
    excluidos_sem_link = 0
    duplicados = 0
    erros_acesso = 0

    for cartao in cartoes:

        municipio_elemento = cartao.find(
            class_="concelho"
        )

        municipio = obter_texto(municipio_elemento)

        if municipio not in MUNICIPIOS:
            excluidos_municipio += 1
            continue

        categoria_elemento = cartao.find(
            class_="categoria"
        )

        categoria = obter_texto(categoria_elemento)

        link_evento = cartao.find(
            "a",
            href=re.compile(r"/evento/")
        )

        if not link_evento:
            excluidos_sem_link += 1
            continue

        url_evento = urljoin(
            URL_AGENDA,
            link_evento["href"]
        )

        if url_evento in urls_processados:
            duplicados += 1
            continue

        urls_processados.add(url_evento)

        titulo_cartao = obter_texto(link_evento)

        data_inicio, data_fim = obter_datas_do_cartao(
            cartao
        )

        if not evento_no_periodo(
            data_inicio,
            data_fim,
            inicio_periodo,
            fim_periodo
        ):
            excluidos_periodo += 1

            print(
                f"\nExcluído por data: {titulo_cartao or url_evento}"
            )

            continue

        print(
            f"\nA analisar: {titulo_cartao or url_evento}"
        )

        try:
            evento, motivo = extrair_evento(
                url_evento,
                municipio,
                categoria,
                data_inicio,
                data_fim
            )

            if evento:
                eventos.append(evento)

                print("  -> Evento aceite.")
                print(
                    f"     Horário: {evento['horario'] or 'Não indicado'}"
                )
                print(
                    f"     Local: {evento['local']}"
                )

            else:
                motivos_exclusao[motivo] = (
                    motivos_exclusao.get(motivo, 0) + 1
                )

                print(f"  -> Evento excluído: {motivo}")

        except requests.RequestException as erro:
            erros_acesso += 1
            print(f"  -> Erro de acesso: {erro}")

        except Exception as erro:
            erros_acesso += 1
            print(f"  -> Erro inesperado: {erro}")

        time.sleep(0.5)

    return (
        eventos,
        inicio_periodo,
        fim_periodo,
        excluidos_periodo,
        excluidos_municipio,
        excluidos_sem_link,
        duplicados,
        erros_acesso,
        motivos_exclusao
    )


# =========================================================
# EXECUÇÃO E CRIAÇÃO DO FICHEIRO JSON
# =========================================================

if __name__ == "__main__":

    (
        eventos,
        inicio_periodo,
        fim_periodo,
        excluidos_periodo,
        excluidos_municipio,
        excluidos_sem_link,
        duplicados,
        erros_acesso,
        motivos_exclusao
    ) = recolher_eventos()

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

    print(
        f"Período analisado: {inicio_periodo} a {fim_periodo}"
    )

    print(f"Eventos aceites: {len(eventos)}")
    print(f"Excluídos por data: {excluidos_periodo}")
    print(f"Excluídos por município: {excluidos_municipio}")
    print(f"Cartões sem ligação para evento: {excluidos_sem_link}")
    print(f"Eventos duplicados: {duplicados}")
    print(f"Erros de acesso ou leitura: {erros_acesso}")

    print("\nMOTIVOS DE EXCLUSÃO NA VALIDAÇÃO:")

    if motivos_exclusao:
        for motivo, quantidade in sorted(
            motivos_exclusao.items(),
            key=lambda item: item[1],
            reverse=True
        ):
            print(f"- {motivo}: {quantidade}")
    else:
        print("- Não foram registadas exclusões na validação.")

    print("\nFicheiro criado: eventos.json")
