import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN VISUAL DEL NAVEGADOR
st.set_page_config(
    page_title="Control de Alumnos - Faustino",
    page_icon="🎓",
    layout="centered"
)

# 2. PROTOCOLO DE CONEXIÓN SEGURO CON SUPABASE (A TRAVÉS DE STREAMLIT SECRETS)
try:
    SUPABASE_URL = "https://cwpispkqdphhiibaqnkb.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cGlzcGtxZHBoaGlpYmFxbmtiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA2MTAxNDIsImV4cCI6MjA5NjE4NjE0Mn0.oXDl9yU5BoYdH1WpVbJWHyVs8w6Lu5F9AxUxJnFl8CE"
    @st.cache_resource
    def conectar_base_datos():
        return create_client(SUPABASE_URL, SUPABASE_KEY)
        
    supabase = conectar_base_datos()
except Exception as e:
    st.error(f"Error crítico al cargar las credenciales de seguridad desde Secrets: {e}")

# 3. ENCABEZADOS DE LA PÁGINA PRINCIPAL
st.title("🎓 Control de Alumnos - Panel Web")
st.markdown("Mantenimiento y Analítica en tiempo real conectado de forma segura a **Supabase Cloud**.")
st.divider()

# 4. MENÚ LATERAL INTERACTIVO DE OPERACIONES
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

# ==============================================================================
# MÓDULO 1: READ - LECTURA DE REGISTROS (VISUALIZACIÓN DE LA TABLA)
# ==============================================================================
if menu_operacion == "📁 Ver Alumnos (Read)":
    st.subheader("Lista Completa de Alumnos")
    try:
        solicitud = supabase.table("ALUMNOS").select("*").execute()
        if solicitud.data:
            st.dataframe(solicitud.data, use_container_width=True)
            st.info(f"Total de alumnos registrados en la base de datos: {len(solicitud.data)}")
        else:
            st.warning("La base de datos se encuentra vacía o no se encontraron registros.")
    except Exception as error:
        st.error(f"Error al intentar descargar la información de Supabase: {error}")

# ==============================================================================
# MÓDULO 2: CREATE - REGISTRO DE NUEVOS ALUMNOS (FORMULARIO TRANSACCIONAL)
# ==============================================================================
elif menu_operacion == "➕ Registrar Nuevo (Create)":
    st.subheader("Formulario de Alta de Estudiantes")
    with st.form("formulario_alta", clear_on_submit=True):
        txt_dni = st.text_input("DNI (8 dígitos requeridos):", max_chars=8)
        col_izq, col_der = st.columns(2)
        with col_izq:
            txt_pat = st.text_input("Apellido Paterno:")
            txt_nom = st.text_input("Nombres Completos:")
        with col_der:
            txt_mat = st.text_input("Apellido Materno (Opcional):")
            opt_sexo = st.selectbox("Sexo del Estudiante:", ["M", "F", "O"])
            
        num_edad = st.number_input("Edad:", min_value=0, max_value=120, value=18, step=1)
        btn_enviar = st.form_submit_button("Guardar Registro", type="primary")
        
        if btn_enviar:
            if not txt_dni or not txt_pat or not txt_nom:
                st.error("Campos obligatorios incompletos (Verifique DNI, Apellido Paterno y Nombre).")
            else:
                try:
                    payload = {
                        "DNI": txt_dni.strip(),
                        "APELLIDO_PAT": txt_pat.strip(),
                        "APELLIDO_MAT": txt_mat.strip() if txt_mat.strip() else None,
                        "NOMBRE": txt_nom.strip(),
                        "SEXO": opt_sexo,
                        "EDAD": int(num_edad)
                    }
                    supabase.table("ALUMNOS").insert(payload).execute()
                    st.success(f"¡Alumno {txt_nom} registrado exitosamente en la nube!")
                except Exception as error:
                    st.error(f"No se pudo guardar el registro en el servidor: {error}")

# ==============================================================================
# MÓDULO 3: UPDATE - ACTUALIZACIÓN DE DATOS (EDICIÓN PARCIAL)
# ==============================================================================
elif menu_operacion == "🔄 Actualizar Datos (Update)":
    st.subheader("Modificación de Información Existente")
    buscar_dni = st.text_input("Ingrese el DNI del alumno a modificar:")
    if buscar_dni:
        try:
            solicitud = supabase.table("ALUMNOS").select("*").eq("DNI", buscar_dni).execute()
            if solicitud.data:
                item = solicitud.data[0]
                st.success("Registro localizado con éxito.")
                with st.form("formulario_edicion"):
                    u_pat = st.text_input("Apellido Paterno:", value=item.get("APELLIDO_PAT", ""))
                    u_mat = st.text_input("Apellido Materno:", value=item.get("APELLIDO_MAT", "") or "")
                    u_nom = st.text_input("Nombres:", value=item.get("NOMBRE", ""))
                    opciones_sexo = ["M", "F", "O"]
                    idx = opciones_sexo.index(item.get("SEXO", "M")) if item.get("SEXO") in opciones_sexo else 0
                    u_sexo = st.selectbox("Sexo:", opciones_sexo, index=idx)
                    u_edad = st.number_input("Edad:", min_value=0, max_value=120, value=int(item.get("EDAD", 18)))
                    
                    if st.form_submit_button("Actualizar Datos", type="primary"):
                        cambios = {
                            "APELLIDO_PAT": u_pat.strip(),
                            "APELLIDO_MAT": u_mat.strip() if u_mat.strip() else None,
                            "NOMBRE": u_nom.strip(),
                            "SEXO": u_sexo,
                            "EDAD": int(u_edad)
                        }
                        supabase.table("ALUMNOS").update(cambios).eq("DNI", buscar_dni).execute()
                        st.success("¡Información actualizada correctamente en la base de datos remota!")
            else:
                st.error("No se encontró ningún alumno registrado con ese número de DNI.")
        except Exception as error:
            st.error(f"Error durante el proceso de edición: {error}")

# ==============================================================================
# MÓDULO 4: DELETE - ELIMINACIÓN DE REGISTROS (BAJA FÍSICA)
# ==============================================================================
elif menu_operacion == "❌ Eliminar Registro (Delete)":
    st.subheader("Dar de Baja Registros del Sistema")
    eliminar_dni = st.text_input("Ingrese el DNI del alumno que desea remover:")
    if eliminar_dni:
        try:
            solicitud = supabase.table("ALUMNOS").select("*").eq("DNI", eliminar_dni).execute()
            if solicitud.data:
                item = solicitud.data[0]
                st.warning(f"¿Está seguro de eliminar permanentemente a: {item['NOMBRE']} {item['APELLIDO_PAT']}?")
                check_seguridad = st.checkbox("Confirmo la eliminación física y permanente del registro.")
                if st.button("Eliminar definitivamente") and check_seguridad:
                    supabase.table("ALUMNOS").delete().eq("DNI", eliminar_dni).execute()
                    st.success("El registro ha sido removido completamente del servidor cloud.")
            else:
                st.error("No se encontró ningún registro coincidente con el DNI proporcionado.")
        except Exception as error:
            st.error(f"Error al intentar ejecutar la baja: {error}")

# ==============================================================================
# MÓDULO 5: ANALÍTICA AVANZADA - INTEGRACIÓN DEL PANEL ESTADÍSTICO (PUNTO 4)
# ==============================================================================
elif menu_operacion == "📊 Reportes y Gráficos (Punto 4)":
    st.subheader("Métricas de Control Demográfico y Reportes Estadísticos")
    try:
        solicitud = supabase.table("ALUMNOS").select("*").execute()
        if solicitud.data:
            # Conversión de la respuesta JSON de Supabase en un Dataframe de Pandas
            df_datos = pd.DataFrame(solicitud.data)
            
            # Casteo numérico preventivo para evitar fallas por datos nulos o corruptos
            df_datos['EDAD'] = pd.to_numeric(df_datos['EDAD'], errors='coerce')
            
            # Despliegue de Indicadores Clave de Rendimiento (KPIs)
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="👥 Cantidad Total de DNI Únicos", value=df_datos['DNI'].nunique())
            with c2:
                promedio = df_datos['EDAD'].mean()
                st.metric(label="📈 Edad Promedio del Alumnado", value=f"{promedio:.1f} años" if pd.notna(promedio) else "N/A")
            
            st.divider()
            
            # GRÁFICO 1: Distribución por Sexo (Gráfico de Tarta / Pie Chart)
            st.markdown("#### 🔄 Distribución de Alumnos por Ítem: SEXO")
            resumen_sexo = df_datos['SEXO'].value_counts().reset_index()
            resumen_sexo.columns = ['Sexo', 'Total Alumnos']
            
            grafico_tarta = px.pie(
                resumen_sexo, values='Total Alumnos', names='Sexo',
                color='Sexo', color_discrete_map={'M':'#3498db', 'F':'#e74c3c', 'O':'#9b59b6'},
                hole=0.2
            )
            st.plotly_chart(grafico_tarta, use_container_width=True)
            
            st.divider()
            
            # GRÁFICO 2: Cantidad de Alumnos por Edad (Gráfico de Barras / Bar Chart)
            st.markdown("#### 📊 Distribución de Alumnos por Ítem: EDAD (Cantidad por Edades)")
            df_limpio = df_datos.dropna(subset=['EDAD'])
            resumen_edad = df_limpio['EDAD'].value_counts().reset_index()
            resumen_edad.columns = ['Edad', 'Número de Alumnos']
            resumen_edad['Edad'] = resumen_edad['Edad'].astype(int)
            resumen_edad = resumen_edad.sort_values(by='Edad')
            
            grafico_barras = px.bar(
                resumen_edad, x='Edad', y='Número de Alumnos', 
                color='Número de Alumnos', color_continuous_scale='Tealgrn',
                labels={'Edad': 'Edad Cronológica', 'Número de Alumnos': 'Cantidad de Estudiantes Total'}
            )
            grafico_barras.update_layout(xaxis=dict(type='category'))
            st.plotly_chart(grafico_barras, use_container_width=True)
            
        else:
            st.warning("No existen registros suficientes en la base de datos para estructurar las gráficas.")
    except Exception as error:
        st.error(f"Error al compilar el módulo analítico automatizado: {error}")
