
import streamlit as st
import json
from pathlib import Path


# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Porto à Borla",
    page_icon="🎟️",
    layout="wide"
)


# =====================================================
# MUNICÍPIOS E CATEGORIAS
# =====================================================

MUNICIPIOS = [
    "Todos os municípios",
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

CATEGORIAS = [
    "Todas as categorias",
    "Música",
    "Exposições",
    "Teatro",
    "Teatro e dança",
    "Cinema",
    "Workshops",
    "Desporto",
    "Feiras e mercados",
    "Feiras e gastronomia",
    "Ar livre",
    "Natureza e ar livre",
    "Conferências",
    "Livros e ideias",
    "Outros"
]


# =====================================================
# LEITURA DOS EVENTOS
# =====================================================

def carregar_eventos():

    ficheiro = Path("eventos.json")

    if not ficheiro.exists():
        return []

    try:
        with open(ficheiro, "r", encoding="utf-8") as f:
            eventos = json.load(f)

        if isinstance(eventos, list):
            return eventos

        return []

    except (json.JSONDecodeError, OSError):
        return []


# =====================================================
# FILTRAGEM DOS EVENTOS
# =====================================================

def filtrar_eventos(eventos, municipio, categoria):

    resultados = []

    for evento in eventos:

        if (
            municipio != "Todos os municípios"
            and evento.get("municipio") != municipio
        ):
            continue

        if (
            categoria != "Todas as categorias"
            and evento.get("categoria") != categoria
        ):
            continue

        resultados.append(evento)

    return resultados


# =====================================================
# APRESENTAÇÃO DA PÁGINA
# =====================================================

st.title("🎟️ Porto à Borla")

st.subheader(
    "Descobre o que fazer gratuitamente no distrito do Porto"
)

st.write(
    "A tua agenda inteligente de eventos, "
    "cultura e atividades gratuitas."
)

st.divider()


# =====================================================
# FILTROS
# =====================================================

col1, col2 = st.columns(2)

with col1:
    municipio = st.selectbox(
        "📍 Município",
        MUNICIPIOS
    )

with col2:
    categoria = st.selectbox(
        "🎭 Categoria",
        CATEGORIAS
    )

st.divider()


# =====================================================
# LISTAGEM DOS EVENTOS
# =====================================================

st.subheader("📅 Próximos eventos")

eventos = carregar_eventos()

eventos_filtrados = filtrar_eventos(
    eventos,
    municipio,
    categoria
)


if not eventos:

    st.info(
        "Ainda não existem eventos disponíveis. "
        "Estamos a preparar a ligação à base de dados."
    )

elif not eventos_filtrados:

    st.warning(
        "Não foram encontrados eventos para os filtros selecionados."
    )

else:

    st.write(
        f"Foram encontrados **{len(eventos_filtrados)} eventos**."
    )

    for evento in eventos_filtrados:

        with st.container(border=True):

            st.markdown(
                f"### {evento.get('titulo', 'Evento sem título')}"
            )

            st.caption(
                f"📍 {evento.get('municipio', '')} "
                f"· {evento.get('categoria', '')}"
            )

            quando = evento.get("quando", "")
            horario = evento.get("horario", "")
            local = evento.get("local", "")

            if quando:
                st.write(f"📅 **Quando:** {quando}")

            if horario:
                st.write(f"🕒 **Horário:** {horario}")

            if local:
                st.write(f"📌 **Local:** {local}")

            detalhe_preco = evento.get("detalhe_preco", "")

            if detalhe_preco:
                st.write(f"🎟️ **Entrada:** {detalhe_preco}")
            else:
                st.write("🎟️ **Entrada gratuita**")

            publico = evento.get("publico", "")

            if publico:
                st.write(f"👥 **Público:** {publico}")

            url_evento = evento.get("url_evento", "")
            fonte_oficial = evento.get("fonte_oficial", "")

            col_a, col_b = st.columns(2)

            with col_a:
                if url_evento:
                    st.markdown(
                        f"[Ver detalhes do evento]({url_evento})"
                    )

            with col_b:
                if fonte_oficial:
                    st.markdown(
                        f"[Consultar fonte oficial]({fonte_oficial})"
                    )


# =====================================================
# RODAPÉ
# =====================================================

st.divider()

st.caption(
    "Porto à Borla | Eventos gratuitos nos 18 municípios "
    "do distrito do Porto."
)
