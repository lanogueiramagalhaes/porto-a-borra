
import streamlit as st
import json
from pathlib import Path


# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Porto à Borla",
    page_icon="🎟️",
    layout="wide"
)

MUNICIPIOS = [
    "Todos os municípios",
    "Amarante", "Baião", "Felgueiras", "Gondomar",
    "Lousada", "Maia", "Marco de Canaveses",
    "Matosinhos", "Paços de Ferreira", "Paredes",
    "Penafiel", "Porto", "Póvoa de Varzim",
    "Santo Tirso", "Trofa", "Valongo",
    "Vila do Conde", "Vila Nova de Gaia"
]

CATEGORIAS = [
    "Todas as categorias",
    "Música", "Exposições", "Teatro", "Teatro e dança",
    "Cinema", "Workshops", "Desporto",
    "Feiras e mercados", "Feiras e gastronomia",
    "Ar livre", "Natureza e ar livre",
    "Conferências", "Livros e ideias", "Outros"
]


# =====================================================
# CARREGAR EVENTOS
# =====================================================

def carregar_eventos():
    ficheiro = Path("eventos.json")

    if not ficheiro.exists():
        return []

    try:
        with open(ficheiro, "r", encoding="utf-8") as f:
            dados = json.load(f)

        return dados if isinstance(dados, list) else []

    except (json.JSONDecodeError, OSError):
        return []


# =====================================================
# FILTRAR EVENTOS
# =====================================================

def filtrar_eventos(eventos, municipio, categoria):
    resultados = []

    for evento in eventos:
        if municipio != "Todos os municípios":
            if evento.get("municipio") != municipio:
                continue

        if categoria != "Todas as categorias":
            if evento.get("categoria") != categoria:
                continue

        resultados.append(evento)

    return resultados


# =====================================================
# APRESENTAÇÃO DE CADA EVENTO
# =====================================================

def apresentar_evento(evento):

    titulo = evento.get("titulo", "Evento sem título")
    municipio = evento.get("municipio", "")
    categoria = evento.get("categoria", "")
    quando = evento.get("quando", "")
    horario = evento.get("horario", "")
    local = evento.get("local", "")
    preco = evento.get("preco", "")
    publico = evento.get("publico", "")
    url_evento = evento.get("url_evento", "")
    fonte_oficial = evento.get("fonte_oficial", "")

    with st.container(border=True):

        st.markdown(f"### {titulo}")

        st.caption(f"📍 {municipio}  ·  🎭 {categoria}")

        if quando:
            st.write(f"📅 **Data e horário:** {quando}")
        elif horario:
            st.write(f"🕒 **Horário:** {horario}")

        if local:
            st.write(f"📌 **Local:** {local}")

        if preco:
            st.write(f"🎟️ **Entrada:** {preco}")
        else:
            st.write("🎟️ **Entrada gratuita**")

        if publico:
            st.write(f"👥 **Público:** {publico}")

        links = []

        if url_evento:
            links.append(f"[Ver detalhes do evento]({url_evento})")

        if fonte_oficial:
            links.append(f"[Consultar fonte oficial]({fonte_oficial})")

        if links:
            st.markdown(" · ".join(links))


# =====================================================
# PÁGINA PRINCIPAL
# =====================================================

st.title("🎟️ Porto à Borla")

st.subheader(
    "Descobre o que fazer gratuitamente no distrito do Porto"
)

st.write(
    "A tua agenda de eventos, cultura e atividades gratuitas."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    municipio = st.selectbox(
        "📍 Escolhe um município",
        MUNICIPIOS
    )

with col2:
    categoria = st.selectbox(
        "🎭 Escolhe uma categoria",
        CATEGORIAS
    )

st.divider()

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
        "A próxima recolha poderá atualizar esta agenda."
    )

elif not eventos_filtrados:
    st.warning(
        "Não foram encontrados eventos para os filtros selecionados."
    )

else:
    st.write(
        f"Encontrámos **{len(eventos_filtrados)} eventos**."
    )

    for evento in eventos_filtrados:
        apresentar_evento(evento)

st.divider()

st.caption(
    "Porto à Borla | Eventos gratuitos nos 18 municípios "
    "do distrito do Porto."
)
