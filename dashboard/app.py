import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import os

# --- CONFIGURACIÓN ---
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

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
col1, col2, col3, col4, col5 = st.columns(5)

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
with col5:
    sin_ssl = len(df[df["tiene_ssl"] == False])
    st.metric("Sin SSL", sin_ssl)

st.divider()

# --- FILTROS ---
st.subheader("Filtros")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    segmentos = ["Todos"] + df["segmento"].dropna().unique().tolist()
    filtro_segmento = st.selectbox("Segmento", segmentos)

with col_f2:
    filtro_score = st.slider("Score máximo", 0, 100, 100)

with col_f3:
    filtro_sin_web = st.checkbox("Solo sin web propia")

# --- APLICAR FILTROS ---
df_filtrado = df.copy()

if filtro_segmento != "Todos":
    df_filtrado = df_filtrado[df_filtrado["segmento"] == filtro_segmento]

if filtro_sin_web:
    df_filtrado = df_filtrado[df_filtrado["website"].isna()]

df_filtrado = df_filtrado[df_filtrado["score"] <= filtro_score]
df_filtrado = df_filtrado.sort_values("score")

# --- TABLA ---
st.subheader(f"Leads encontrados: {len(df_filtrado)}")

st.dataframe(
    df_filtrado[[
        "name", "score", "segmento", "website",
        "tiene_ssl", "es_responsive", "tiene_reservas",
        "cms_detectado", "tiempo_carga_ms",
        "phone", "rating", "reviews_count", "city"
    ]],
    use_container_width=True,
    column_config={
        "name": "Negocio",
        "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100),
        "segmento": "Segmento",
        "website": st.column_config.LinkColumn("Web"),
        "tiene_ssl": st.column_config.CheckboxColumn("SSL"),
        "es_responsive": st.column_config.CheckboxColumn("Mobile"),
        "tiene_reservas": st.column_config.CheckboxColumn("Reservas"),
        "cms_detectado": "CMS",
        "tiempo_carga_ms": st.column_config.NumberColumn("Carga (ms)", format="%d ms"),
        "phone": "Teléfono",
        "rating": st.column_config.NumberColumn("Rating", format="⭐ %.1f"),
        "reviews_count": "Reseñas",
        "city": "Ciudad"
    },
    hide_index=True
)

# --- DETALLE DE UN LEAD ---
st.divider()
st.subheader("🔍 Detalle de carencias")

nombres = df_filtrado["name"].dropna().tolist()
seleccionado = st.selectbox("Selecciona un negocio", nombres)

if seleccionado:
    negocio = df_filtrado[df_filtrado["name"] == seleccionado].iloc[0]
    carencias = negocio.get("carencias") or []

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.write(f"**Web:** {negocio.get('website') or 'Sin web'}")
        st.write(f"**Teléfono:** {negocio.get('phone') or 'Sin teléfono'}")
        st.write(f"**Rating:** ⭐ {negocio.get('rating')}")
        st.write(f"**Reseñas:** {negocio.get('reviews_count')}")
        st.write(f"**CMS:** {negocio.get('cms_detectado') or 'N/A'}")

    with col_d2:
        st.write(f"**SSL:** {'✅' if negocio.get('tiene_ssl') else '❌'}")
        st.write(f"**Mobile:** {'✅' if negocio.get('es_responsive') else '❌'}")
        st.write(f"**Formulario:** {'✅' if negocio.get('tiene_formulario') else '❌'}")
        st.write(f"**Reservas:** {'✅' if negocio.get('tiene_reservas') else '❌'}")
        st.write(f"**Carga:** {negocio.get('tiempo_carga_ms') or 'N/A'} ms")

    if carencias:
        st.write("**Carencias detectadas:**")
        for c in carencias:
            st.error(f"{c['gravedad']} {c['mensaje']} → 💼 {c['servicio']}")