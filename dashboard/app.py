import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import os

# --- CONFIGURACIÓN ---
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="DigitalScope",
    page_icon="🔭",
    layout="wide"
)

# --- CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_datos():
    response = supabase.table("businesses").select("*").execute()
    return pd.DataFrame(response.data)

df = cargar_datos()

# --- CABECERA ---
st.title("🔭 DigitalScope")
st.caption("Detección de oportunidades tecnológicas en negocios locales de Sevilla")
st.divider()

# --- MÉTRICAS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total negocios", len(df))
with col2:
    calientes = len(df[df["segmento"] == "🔥 LEAD CALIENTE"])
    st.metric("Leads calientes", calientes)
with col3:
    tibios = len(df[df["segmento"] == "🌤️ LEAD TIBIO"])
    st.metric("Leads tibios", tibios)
with col4:
    sin_web = len(df[df["website"].isna()])
    st.metric("Sin web propia", sin_web)

st.divider()

# --- FILTROS ---
st.subheader("Filtros")
col_f1, col_f2 = st.columns(2)

with col_f1:
    segmentos = ["Todos"] + df["segmento"].dropna().unique().tolist()
    filtro_segmento = st.selectbox("Segmento", segmentos)

with col_f2:
    filtro_score = st.slider("Score máximo", 0, 100, 100)

# --- APLICAR FILTROS ---
df_filtrado = df.copy()

if filtro_segmento != "Todos":
    df_filtrado = df_filtrado[df_filtrado["segmento"] == filtro_segmento]

df_filtrado = df_filtrado[df_filtrado["score"] <= filtro_score]
df_filtrado = df_filtrado.sort_values("score")

# --- TABLA ---
st.subheader(f"Leads encontrados: {len(df_filtrado)}")

st.dataframe(
    df_filtrado[["name", "score", "segmento", "website", "phone", "rating", "reviews_count", "city"]],
    use_container_width=True,
    column_config={
        "name": "Negocio",
        "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100),
        "segmento": "Segmento",
        "website": st.column_config.LinkColumn("Web"),
        "phone": "Teléfono",
        "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
        "reviews_count": "Reseñas",
        "city": "Ciudad"
    },
    hide_index=True
)