
import streamlit as st

st.set_page_config(
    page_title="Porto à Borla",
    page_icon="🎟️",
    layout="wide"
)

st.title("🎟️ Porto à Borla")
st.subheader("Descobre o que fazer gratuitamente no distrito do Porto")

st.write(
    "A tua agenda inteligente de eventos, "
    "cultura e atividades gratuitas."
)

municipios = [
    "Todos os municípios",
    "Amarante", "Baião", "Felgueiras", "Gondomar",
    "Lousada", "Maia", "Marco de Canaveses",
    "Matosinhos", "Paços de Ferreira", "Paredes",
    "Penafiel", "Porto", "Póvoa de Varzim",
    "Santo Tirso", "Trofa", "Valongo",
    "Vila do Conde", "Vila Nova de Gaia"
]

categorias = [
    "Todas as categorias",
    "Música", "Exposições", "Teatro",
    "Cinema", "Workshops", "Desporto",
    "Feiras e mercados", "Ar livre",
    "Conferências", "Outros"
]

st.divider()

col1, col2 = st.columns(2)

with col1:
    municipio = st.selectbox(
        "📍 Município",
        municipios
    )

with col2:
    categoria = st.selectbox(
        "🎭 Categoria",
        categorias
    )

st.divider()

st.subheader("📅 Próximos eventos")

st.info(
    "Estamos a preparar a tua agenda! "
    "Os eventos serão apresentados aqui "
    "depois de ligarmos as fontes de informação."
)

st.divider()

st.caption(
    "Porto à Borla | Eventos gratuitos no distrito do Porto"
)
