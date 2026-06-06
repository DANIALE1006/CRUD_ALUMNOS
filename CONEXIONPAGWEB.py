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

# 2. PROTOCOLO DE CONEXIÓN CON SUPABASE (USANDO SECRETS)
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    
    @st.cache_resource
    def conectar_base_datos():
        return create_client(SUPABASE_URL, SUPABASE_KEY)
        
    supabase = conectar_base_datos()
except Exception as e:
    st.error(f"Error de enlace con las credenciales seguras: {e}")

# 3. ENCABEZADOS DE LA PÁGINA
st.title("🎓 Control de Alumnos - Panel Web")
st.markdown("Mantenimiento y Analítica en tiempo real conectado a **Supabase**.")
st.divider()

# 4. MENÚ LATERAL INTERACTIVO
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
# MÓDULO 1: READ (VER ALUMNOS)
# ==========================================
if menu_operacion == "📁 Ver Alumnos (Read)":
    st.subheader("Lista Completa de Alumnos")
    try:
        solicitud = supabase.table("ALUMNOS").select("*").order("APELLIDO_PAT").execute()
        if solicitud.data:
            st.dataframe(solicitud.data, use_container_width=True)
            st.info(f"Total de alumnos registrados: {len(solicitud.data)}")
        else:
            st.warning("No se encontraron registros en la tabla.")
    except Exception as error:
        st.error(f"Error al descargar la información: {error}")

# ==========================================
# MÓDULO 2: CREATE (REGISTRAR NUEVO)
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
                        "NOMBRE": txt_nom.strip(),
                        "SEXO": opt_sexo,
                        "EDAD": int(num_edad)
                    }
                    supabase.table("ALUMNOS").insert(payload).execute()
                    st.success(f"¡Alumno {txt_nom} registrado exitosamente!")
                except Exception as error:
                    st.error(f"No se pudo guardar el registro: {error}")

# ==========================================
# MÓDULO 3: UPDATE (MODIFICAR DATOS)
# ==========================================
elif menu_operacion == "🔄 Actualizar Datos (Update)":
    st.subheader("Actualizar Información de Alumno")
    buscar_dni = st.text_input("Ingrese el DNI del alumno a modificar:")
    if buscar_dni:
        try:
            solicitud = supabase.table("ALUMNOS").select("*").eq("DNI", buscar_dni).execute()
            if solicitud.data:
                item = solicitud.data[0]
                st.success("Registro localizado.")
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
                        st.success("¡Información actualizada en la base de datos!")
            else:
                st.error("No se encontró ningún alumno con ese DNI.")
        except Exception as error:
            st.error(f"Error en la edición: {error}")

# ==========================================
# MÓAULO 4: DELETE (ELIMINAR ALUMNO)
# ==========================================
elif menu_operacion == "❌ Eliminar Registro (Delete)":
    st.subheader("Dar de Baja a un Alumno")
    eliminar_dni = st.text_input("Ingrese el DNI del alumno que desea borrar:")
    if eliminar_dni:
        try:
            solicitud = supabase.table("ALUMNOS").select("*").eq("DNI", eliminar_dni).execute()
            if solicitud.data:
                item = solicitud.data[0]
                st.warning(f"¿Desea eliminar permanentemente a: {item['NOMBRE']} {item['APELLIDO_PAT']}?")
                check_seguridad = st.checkbox("Confirmo la eliminación física del registro.")
                if st.button("Eliminar definitivamente") and check_seguridad:
                    supabase.table("ALUMNOS").delete().eq("DNI", eliminar_dni).execute()
                    st.success("El registro ha sido removido del sistema cloud.")
            else:
                st.error("No se encontró ningún registro coincidente.")
        except Exception as error:
            st.error(f"Error al eliminar: {error}")

# ==========================================
# MÓDULO 5: REPORTE Y GRÁFICOS INTERACTIVOS
# ==========================================
elif menu_operacion == "📊 Reportes y Gráficos (Punto 4)":
    st.subheader("Métricas y Estadísticas con todos los Ítems Registrados")
    try:
        solicitud = supabase.table("ALUMNOS").select("*").execute()
        if solicitud.data:
            df_datos = pd.DataFrame(solicitud.data)
            df_datos['EDAD'] = pd.to_numeric(df_datos['EDAD'], errors='coerce')
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="👥 Cantidad Total de DNI Únicos", value=df_datos['DNI'].nunique())
            with c2:
                promedio = df_datos['EDAD'].mean()
                st.metric(label="📈 Edad Promedio del Alumnado", value=f"{promedio:.1f} años" if pd.notna(promedio) else "N/A")
            
            st.divider()
            
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
            
            st.markdown("#### 📊 Distribución de Alumnos por Ítem: EDAD")
            df_limpio = df_datos.dropna(subset=['EDAD'])
            resumen_edad = df_limpio['EDAD'].value_counts().reset_index()
            resumen_edad.columns = ['Edad', 'Número de Alumnos']
            resumen_edad['Edad'] = resumen_edad['Edad'].astype(int)
            resumen_edad = resumen_edad.sort_values(by='Edad')
            
            grafico_barras = px.bar(
                resumen_edad, x='Edad', y='Número de Alumnos', 
                color='Número de Alumnos', color_continuous_scale='Tealgrn'
            )
            grafico_barras.update_layout(xaxis=dict(type='category'))
            st.plotly_chart(grafico_barras, use_container_width=True)
            
        else:
            st.warning("No hay registros suficientes para estructurar las gráficas.")
    except Exception as error:
        st.error(f"Error al compilar el módulo analítico: {error}")
