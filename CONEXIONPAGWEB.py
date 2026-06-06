import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DEL ENTORNO WEB
st.set_page_config(
    page_title="Control de Alumnos",
    page_icon="🎓",
    layout="centered"
)

# 2. CREDENCIALES DE AUTENTICACIÓN (API)
URL_BD = "https://cwpispkqdphhiibaqnkb.supabase.co"
KEY_BD = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpcCI6IiJzdXBhYmFzZS5jby" # Coloca tu clave anon completa aquí si se recortó

@st.cache_resource
def conectar_base_datos():
    return create_client(URL_BD, KEY_BD)

try:
    supabase = conectar_base_datos()
except Exception as e:
    st.error(f"Error de enlace con el servidor backend: {e}")

# 3. INTERFAZ Y ENCABEZADOS
st.title("🎓 Control de Alumnos - Panel Web")
st.markdown("Mantenimiento y Analítica en tiempo real conectado a **Supabase**.")
st.divider()

# 4. PANEL DE NAVEGACIÓN LATERAL
menu_operacion = st.sidebar.selectbox(
    "Selecciona una Operación",
    [
        "📁 Ver Alumnos (Read)", 
        "➕ Registrar Nuevo (Create)", 
        "🔄 Actualizar Datos (Update)", 
        "❌ Eliminar Registro (Delete)",
        "📊 Reportes y Gráficos (Punto 4)"
    ]
)

# ==========================================
# MÓDULO 1: READ (LECTURA TABULAR)
# ==========================================
if menu_operacion == "📁 Ver Alumnos (Read)":
    st.subheader("Lista Completa de Alumnos")
    try:
        solicitud = supabase.table("ALUMNOS").select("*").order("APELLIDO_PAT").execute()
        if solicitud.data:
            st.dataframe(solicitud.data, width="stretch")
            st.info(f"Total de alumnos registrados: {len(solicitud.data)}")
        else:
            st.warning("No se encontraron registros en la tabla.")
    except Exception as error:
        st.error(f"Error al descargar la información: {error}")

# ==========================================
# MÓDULO 2: CREATE (INSERCIÓN)
# ==========================================
elif menu_operacion == "➕ Registrar Nuevo (Create)":
    st.subheader("Formulario de Registro")
    with st.form("formulario_alta", clear_on_submit=True):
        txt_dni = st.text_input("DNI (8 dígitos):", max_chars=8)
        col_izq, col_der = st.columns(2)
        with col_izq:
            txt_pat = st.text_input("Apellido Paterno:")
            txt_nom = st.text_input("Nombres:")
        with col_der:
            txt_mat = st.text_input("Apellido Materno (Opcional):")
            opt_sexo = st.selectbox("Sexo:", ["M", "F", "O"])
            
        num_edad = st.number_input("Edad:", min_value=0, max_value=120, value=18, step=1)
        btn_enviar = st.form_submit_button("Guardar Alumno", type="primary")
        
        if btn_enviar:
            if not txt_dni or not txt_pat or not txt_nom:
                st.error("Campos obligatorios incompletos (DNI, Apellido Paterno y Nombres).")
            else:
                try:
                    payload = {
                        "DNI": txt_dni.strip(),
                        "APELLIDO_PAT": txt_pat.strip(),
                        "APELLIDO_MAT": txt_mat.strip() if txt_mat.strip() else None,
                        "NOMBRE": txt_nom.strip
