
# PORTO À BORLA
# Módulo responsável pela organização dos eventos.

MUNICIPIOS = [
    "Amarante", "Baião", "Felgueiras", "Gondomar",
    "Lousada", "Maia", "Marco de Canaveses",
    "Matosinhos", "Paços de Ferreira", "Paredes",
    "Penafiel", "Porto", "Póvoa de Varzim",
    "Santo Tirso", "Trofa", "Valongo",
    "Vila do Conde", "Vila Nova de Gaia"
]

CATEGORIAS = [
    "Música",
    "Exposições",
    "Teatro",
    "Cinema",
    "Workshops",
    "Desporto",
    "Feiras e mercados",
    "Ar livre",
    "Conferências",
    "Outros"
]


def obter_eventos():
    """
    Devolve os eventos recolhidos pelas fontes.

    Por enquanto, não existem eventos recolhidos.
    Não introduzimos exemplos fictícios.
    """
    return []


def filtrar_eventos(eventos, municipio=None, categoria=None):
    """Filtra os eventos por município e categoria."""

    resultados = eventos

    if municipio and municipio != "Todos os municípios":
        resultados = [
            evento for evento in resultados
            if evento.get("municipio") == municipio
        ]

    if categoria and categoria != "Todas as categorias":
        resultados = [
            evento for evento in resultados
            if evento.get("categoria") == categoria
        ]

    return resultados
