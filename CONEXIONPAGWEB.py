import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(
    page_title="Sistema de Gestión Académica",
    page_icon="🎓",
    layout="centered"
)

# --- CONEXIÓN A SUPABASE ---
# NOTA: Tus llaves reales ya están configuradas en tu archivo local
SUPABASE_URL = "https://cwpispkqdphhiibaqnkb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpcCI6IiJzdXBhYmFzZS5jby" # Coloca tu clave real aquí

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")

# --- TÍTULO DE LA APLICACIÓN WEB ---
st.title("🎓 Control de Alumnos - Panel Web")
st.markdown("Mantenimiento y Analítica en tiempo real conectado a **Supabase**.")
st.divider()

# --- MENÚ LATERAL DE NAVEGACIÓN ---
opcion = st.sidebar.selectbox(
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
# 1. READ: VER TODOS LOS ALUMNOS
# ==========================================
if opcion == "📁 Ver Alumnos (Read)":
    st.subheader("Lista Completa de Alumnos")
    try:
        response = supabase.table("ALUMNOS").select("*").order("APELLIDO_PAT").execute()
        if response.data:
            st.dataframe(response.data, width="stretch")
            st.info(f"Total de alumnos registrados: {len(response.data)}")
        else:
            st.warning("No hay alumnos registrados todavía.")
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")

# ==========================================
# 2. CREATE: REGISTRAR UN NUEVO ALUMNO
# ==========================================
elif opcion == "➕ Registrar Nuevo (Create)":
    st.subheader("Formulario de Registro")
    with st.form("form_registro", clear_on_submit=True):
        dni = st.text_input("DNI (8 dígitos):", max_chars=8)
        col1, col2 = st.columns(2)
        with col1:
            apellido_pat = st.text_input("Apellido Paterno:")
            nombre = st.text_input("Nombres:")
        with col2:
            apellido_mat = st.text_input("Apellido Materno (Opcional):")
            sexo = st.selectbox("Sexo:", ["M", "F", "O"])
            
        edad = st.number_input("Edad:", min_value=0, max_value=120, value=18, step=1)
        btn_guardar = st.form_submit_button("Guardar Alumno", type="primary")
        
        if btn_guardar:
            if not dni or not apellido_pat or not nombre:
                st.error("Por favor, complete los campos obligatorios (DNI, Apellido Paterno y Nombres).")
            else:
                try:
                    nuevo_alumno = {
                        "DNI": dni.strip(),
                        "APELLIDO_PAT": apellido_pat.strip(),
                        "APELLIDO_MAT": apellido_mat.strip() if apellido_mat.strip() else None,
                        "NOMBRE": nombre.strip(),
                        "SEXO": sexo,
                        "EDAD": int(edad)
                    }
                    supabase.table("ALUMNOS").insert(nuevo_alumno).execute()
                    st.success(f"¡Alumno {nombre} registrado con éxito!")
                except Exception as e:
                    st.error(f"No se pudo registrar: {e}")

# ==========================================
# 3. UPDATE: ACTUALIZAR DATOS
# ==========================================
elif opcion == "🔄 Actualizar Datos (Update)":
    st.subheader("Actualizar Información de Alumno")
    dni_buscar = st.text_input("Ingrese el DNI del alumno a modificar:")
    if dni_buscar:
        try:
            response = supabase.table("ALUMNOS").select("*").eq("DNI", dni_buscar).execute()
            if response.data:
                alumno = response.data[0]
                st.success("Alumno encontrado. Modifique los campos necesarios:")
                with st.form("form_actualizar"):
                    nuevo_pat = st.text_input("Apellido Paterno:", value=alumno.get("APELLIDO_PAT", ""))
                    nuevo_mat = st.text_input("Apellido Materno:", value=alumno.get("APELLIDO_MAT", "") or "")
                    nuevo_nom = st.text_input("Nombres:", value=alumno.get("NOMBRE", ""))
                    lista_sexo = ["M", "F", "O"]
                    idx_sexo = lista_sexo.index(alumno.get("SEXO", "M")) if alumno.get("SEXO") in lista_sexo else 0
                    nuevo_sexo = st.selectbox("Sexo:", lista_sexo, index=idx_sexo)
                    nueva_edad = st.number_input("Edad:", min_value=0, max_value=120, value=int(alumno.get("EDAD", 18)))
                    
                    btn_actualizar = st.form_submit_button("Actualizar Datos", type="primary")
                    if btn_actualizar:
                        datos_modificados = {
                            "APELLIDO_PAT": nuevo_pat.strip(),
                            "APELLIDO_MAT": nuevo_mat.strip() if nuevo_mat.strip() else None,
                            "NOMBRE": nuevo_nom.strip(),
                            "SEXO": nuevo_sexo,
                            "EDAD": int(nueva_edad)
                        }
                        supabase.table("ALUMNOS").update(datos_modificados).eq("DNI", dni_buscar).execute()
                        st.success("¡Datos actualizados correctamente!")
            else:
                st.error("No se encontró ningún alumno con ese DNI.")
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# 4. DELETE: ELIMINAR REGISTRO
# ==========================================
elif opcion == "❌ Eliminar Registro (Delete)":
    st.subheader("Dar de Baja a un Alumno")
    dni_eliminar = st.text_input("Ingrese el DNI del alumno que desea borrar:")
    if dni_eliminar:
        try:
            response = supabase.table("ALUMNOS").select("*").eq("DNI", dni_eliminar).execute()
            if response.data:
                alumno = response.data[0]
                st.warning(f"¿Está seguro de eliminar a: **{alumno['NOMBRE']} {alumno['APELLIDO_PAT']}**?")
                confirmar = st.checkbox("Sí, confirmo que deseo borrar este registro.")
                btn_eliminar = st.button("Eliminar permanentemente")
                if btn_eliminar and confirmar:
                    supabase.table("ALUMNOS").delete().eq("DNI", dni_eliminar).execute()
                    st.success("El alumno ha sido borrado de la base de datos.")
            else:
                st.error("No se encontró ningún alumno con ese DNI.")
        except Exception as e:
            st.error(f"Error: {e}")
# ==========================================
# 5. PUNTO 4: VISUALIZACIONES GRÁFICAS TOTALES
# ==========================================
elif opcion == "📊 Reportes y Gráficos (Punto 4)":
    st.subheader("Métricas y Estadísticas con todos los Ítems Registrados")
    
    try:
        response = supabase.table("ALUMNOS").select("*").execute()
        if response.data:
            # Convertimos todos los ítems de la base de datos a un DataFrame
            df = pd.DataFrame(response.data)
            
            # --- ¡AQUÍ ESTÁ LA CORRECCIÓN! ---
            # Forzamos a que la columna EDAD se convierta a números para evitar el error
            df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce')
            
            # --- ANÁLISIS DE DNI Y EDAD (Métricas rápidas) ---
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="👥 Cantidad Total de DNI Únicos", value=df['DNI'].nunique())
            with col2:
                # Calculamos el promedio ignorando si hay algún dato vacío
                edad_promedio = df['EDAD'].mean()
                if pd.notna(edad_promedio):
                    st.metric(label="📈 Edad Promedio del Alumnado", value=f"{edad_promedio:.1f} años")
                else:
                    st.metric(label="📈 Edad Promedio del Alumnado", value="N/A")
            
            st.divider()
            
            # --- ANÁLISIS DE SEXO (Gráfico de Pastel) ---
            st.markdown("#### 🔄 Distribución de Alumnos por Ítem: SEXO")
            df_sexo = df['SEXO'].value_counts().reset_index()
            df_sexo.columns = ['Sexo', 'Total Alumnos']
            
            fig_pie = px.pie(df_sexo, values='Total Alumnos', names='Sexo',
                             color='Sexo', color_discrete_map={'M':'#3498db', 'F':'#e74c3c', 'O':'#9b59b6'},
                             hole=0.2)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.divider()
            
            # --- ANÁLISIS DE EDAD (Gráfico de Barras) ---
            st.markdown("#### 📊 Distribución de Alumnos por Ítem: EDAD")
            
            # Eliminamos filas que no tengan edad válida para el gráfico de barras
            df_edad_filtrado = df.dropna(subset=['EDAD'])
            df_edad = df_edad_filtrado['EDAD'].value_counts().reset_index()
            df_edad.columns = ['Edad', 'Número de Alumnos']
            
            # Nos aseguramos de que la edad se muestre como entero en el eje X
            df_edad['Edad'] = df_edad['Edad'].astype(int)
            df_edad = df_edad.sort_values(by='Edad')
            
            fig_bar = px.bar(df_edad, x='Edad', y='Número de Alumnos', 
                             labels={'Edad': 'Edad Registrada', 'Número de Alumnos': 'Cantidad de Estudiantes'},
                             color='Número de Alumnos', color_continuous_scale='Tealgrn')
            
            # Forzamos a que el eje X muestre los números uno por uno (como tu gráfico base)
            fig_bar.update_layout(xaxis=dict(type='category'))
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.divider()
            
            # --- ANÁLISIS DE NOMBRES Y APELLIDOS (Top Informativo) ---
            st.markdown("#### 📝 Listado Analítico de Control (Nombres y Apellidos)")
            df['Nombre Completo'] = df['APELLIDO_PAT'] + " " + df['NOMBRE']
            df_lista = df[['DNI', 'Nombre Completo', 'SEXO', 'EDAD']].sort_values(by='Nombre Completo')
            st.dataframe(df_lista, width="stretch")
            
        else:
            st.warning("No hay datos en la base de datos para generar los gráficos.")
    except Exception as e:
        st.error(f"Error al generar las visualizaciones: {e}")

