
import streamlit as st
import json
from pathlib import Path
from datetime import date, datetime, timedelta


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
# CONVERTER DATAS
# =====================================================

def converter_data(valor):

    if not valor:
        return None

    try:
        return datetime.fromisoformat(
            valor.replace("Z", "+00:00")
        ).date()

    except (ValueError, TypeError):
        try:
            return date.fromisoformat(valor[:10])
        except (ValueError, TypeError):
            return None


# =====================================================
# FILTRAR EVENTOS
# =====================================================

def filtrar_eventos(
    eventos,
    municipio,
    categoria,
    pesquisa,
    data_inicio_filtro,
    data_fim_filtro
):

    resultados = []

    for evento in eventos:

        # Filtro por município
        if municipio != "Todos os municípios":
            if evento.get("municipio") != municipio:
                continue

        # Filtro por categoria
        if categoria != "Todas as categorias":
            if evento.get("categoria") != categoria:
                continue

        # Pesquisa por nome
        if pesquisa:
            titulo = evento.get("titulo", "").lower()

            if pesquisa.lower() not in titulo:
                continue

        # Filtro por período
        if data_inicio_filtro and data_fim_filtro:

            inicio_evento = converter_data(
                evento.get("data_inicio")
            )

            fim_evento = converter_data(
                evento.get("data_fim")
            )

            if not inicio_evento or not fim_evento:
                continue

            # O evento tem de decorrer em pelo menos
            # um dia dentro do período selecionado.
            if (
                inicio_evento > data_fim_filtro
                or fim_evento < data_inicio_filtro
            ):
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
    detalhe_preco = evento.get("detalhe_preco", "")
    publico = evento.get("publico", "")
    url_evento = evento.get("url_evento", "")
    fonte_oficial = evento.get("fonte_oficial", "")

    with st.container(border=True):

        st.markdown(f"### {titulo}")

        st.caption(
            f"📍 {municipio}  ·  🎭 {categoria}"
        )

        if quando:
            st.write(f"📅 **Data e horário:** {quando}")
        elif horario:
            st.write(f"🕒 **Horário:** {horario}")

        if local:
            st.write(f"📌 **Local:** {local}")

        # Informação sobre a entrada
        texto_preco = f"{preco} {detalhe_preco}".strip()
        preco_lower = texto_preco.lower()

        st.write("🎟️ **Entrada:** Gratuita")

        if "inscrição" in preco_lower or "inscricao" in preco_lower:
            st.caption("ℹ️ É necessária inscrição prévia.")

        if "lotação limitada" in preco_lower or "lotacao limitada" in preco_lower:
            st.caption("ℹ️ Atividade sujeita a lotação limitada.")

        if "reserva" in preco_lower:
            st.caption("ℹ️ Consulta as condições de reserva.")

        if publico:
            st.write(f"👥 **Público:** {publico}")

        # Ligações
        links = []

        if url_evento:
            links.append(
                f"[Ver detalhes do evento]({url_evento})"
            )

        if fonte_oficial:
            links.append(
                f"[Consultar fonte oficial]({fonte_oficial})"
            )

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


# =====================================================
# PESQUISA
# =====================================================

st.subheader("🔎 Encontra o teu próximo evento")

pesquisa = st.text_input(
    "Pesquisar por nome do evento",
    placeholder="Ex.: caminhada, música, teatro..."
)


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


# =====================================================
# FILTRO POR DATA
# =====================================================

with st.expander("📅 Filtrar por período"):

    ativar_filtro_data = st.checkbox(
        "Quero escolher as datas dos eventos"
    )

    data_inicio_filtro = None
    data_fim_filtro = None

    if ativar_filtro_data:

        hoje = date.today()

        col_data1, col_data2 = st.columns(2)

        with col_data1:
            data_inicio_filtro = st.date_input(
                "Data inicial",
                value=hoje,
                format="DD/MM/YYYY"
            )

        with col_data2:
            data_fim_filtro = st.date_input(
                "Data final",
                value=hoje + timedelta(days=7),
                min_value=data_inicio_filtro,
                format="DD/MM/YYYY"
            )


st.divider()


# =====================================================
# APRESENTAÇÃO DOS EVENTOS
# =====================================================

st.subheader("📅 Próximos eventos")

eventos = carregar_eventos()

if ativar_filtro_data and data_inicio_filtro > data_fim_filtro:

    st.warning(
        "A data final não pode ser anterior à data inicial."
    )

else:

    eventos_filtrados = filtrar_eventos(
        eventos,
        municipio,
        categoria,
        pesquisa,
        data_inicio_filtro if ativar_filtro_data else None,
        data_fim_filtro if ativar_filtro_data else None
    )

    if not eventos:

        st.info(
            "Ainda não existem eventos disponíveis. "
            "A próxima recolha poderá atualizar esta agenda."
        )

    elif not eventos_filtrados:

        st.warning(
            "Não foram encontrados eventos com os critérios selecionados."
        )

    else:

        st.write(
            f"Encontrámos **{len(eventos_filtrados)} eventos**."
        )

        for evento in eventos_filtrados:
            apresentar_evento(evento)


# =====================================================
# RODAPÉ
# =====================================================

st.divider()

st.caption(
    "Porto à Borla | Eventos gratuitos nos 18 municípios "
    "do distrito do Porto."
)
