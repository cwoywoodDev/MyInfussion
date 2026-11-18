import streamlit as st
from ui.views import (
    render_consultor,
    render_formulario_registro,
    render_editar_receta,
    render_admin,
)

# =========================================================
# ⚙️ CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="Botica Herbal • Recetario",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 🎨 PALETA BOTÁNICA LUMINOSA Y ENERGÉTICA
# =========================================================
BG_CREMA = "#F4F2EC"        # Fondo principal cálido (no cansa la vista)
BG_CARD = "#FFFFFF"         # Superficie limpia de tarjetas
ROSA_SUAVE = "#E8CBD0"      # Contenedores suaves y acentos pastel
ROSA_FLORAL = "#D8A2B6"     # Detalles alegres
FRAMBUESA = "#BC7087"       # Acento vibrante cálido
CIRUELA_MED = "#833A5E"     # Subtítulos y etiquetas
BORDO_PROFUNDO = "#591721"  # Alertas y cuidados
VERDE_BOSQUE = "#2E5558"    # Títulos principales y botones
VERDE_SALVIA = "#638E8E"    # Acento botánico secundario
TEXTO_OSCURO = "#261E37"    # Texto principal de alta legibilidad

st.markdown(f"""
<style>
    /* Fondo general de la app */
    .stApp {{
        background-color: {BG_CREMA};
        color: {TEXTO_OSCURO};
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(244, 242, 236, 0.85);
    }}

    /* Barra lateral */
    [data-testid="stSidebar"] {{
        background-color: {ROSA_SUAVE}66;
        border-right: 1px solid {ROSA_FLORAL};
    }}
    [data-testid="stSidebar"] * {{
        color: {TEXTO_OSCURO};
    }}

    /* Etiquetas y textos generales */
    label, .stMarkdown p, .stMarkdown li {{
        color: {TEXTO_OSCURO} !important;
    }}

    /* Inputs y Selectbox claros y limpios */
    .stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {{
        background-color: {BG_CARD} !important;
        color: {TEXTO_OSCURO} !important;
        border: 1px solid {VERDE_SALVIA}88 !important;
        border-radius: 8px !important;
    }}

    /* Tarjeta principal de encabezado de receta */
    .receta-card {{
        background: linear-gradient(135deg, {BG_CARD} 0%, {ROSA_SUAVE}55 100%);
        border: 1px solid {ROSA_FLORAL};
        border-left: 6px solid {VERDE_BOSQUE};
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 12px rgba(38, 30, 55, 0.06);
    }}

    /* Etiqueta de horario */
    .badge-horario {{
        background-color: {FRAMBUESA};
        color: #FFFFFF !important;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}

    /* Caja de Beneficios (Tono verde salvia luminoso) */
    .beneficio-box {{
        background-color: {BG_CARD};
        border: 1px solid {VERDE_SALVIA}88;
        border-top: 4px solid {VERDE_BOSQUE};
        border-radius: 10px;
        padding: 16px;
        margin-top: 12px;
        height: 100%;
        box-shadow: 0 3px 10px rgba(46, 85, 88, 0.06);
    }}

    /* Caja de Cuidados (Tono rosa / frambuesa cálido) */
    .alerta-cuidado {{
        background-color: {ROSA_SUAVE}4D;
        border: 1px solid {FRAMBUESA}88;
        border-top: 4px solid {CIRUELA_MED};
        border-radius: 10px;
        padding: 16px;
        margin-top: 12px;
        height: 100%;
        box-shadow: 0 3px 10px rgba(131, 58, 94, 0.06);
    }}

    /* Botones primarios */
    .stButton > button[kind="primary"], .stFormSubmitButton > button {{
        background-color: {VERDE_BOSQUE} !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.2s ease;
    }}
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {{
        background-color: {FRAMBUESA} !important;
        color: #FFFFFF !important;
    }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 🧭 NAVEGACIÓN LATERAL
# =========================================================
with st.sidebar:
    st.markdown(f"<h2 style='color: {VERDE_BOSQUE}; margin-bottom: 0;'>🌿 Botica Herbal</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {CIRUELA_MED}; font-size: 0.9em; margin-top: 2px; font-weight: 500;'>Recetario & Consultor Fitoterapéutico</p>", unsafe_allow_html=True)
    st.write("---")

    opcion = st.radio(
        "Navegación:",
        [
            "🍵 Consultar Recetas",
            "📝 Registrar Nueva Receta",
            "✏️ Editar Receta",
            "🗂️ Administrar Base de Datos",
        ],
        label_visibility="collapsed",
    )

if opcion == "🍵 Consultar Recetas":
    render_consultor()
elif opcion == "📝 Registrar Nueva Receta":
    render_formulario_registro()
elif opcion == "✏️ Editar Receta":
    render_editar_receta()
elif opcion == "🗂️ Administrar Base de Datos":
    render_admin()