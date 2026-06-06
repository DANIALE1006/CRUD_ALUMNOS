import streamlit as st
from supabase import create_client, Client

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(
    page_title="Sistema de Gestión Académica",
    page_icon="🎓",
    layout="centered"
)

# --- CONEXIÓN A SUPABASE ---
SUPABASE_URL = "https://cwpispkqdphhiibaqnkb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3cGlzcGtxZHBoaGlpYmFxbmtiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA2MTAxNDIsImV4cCI6MjA5NjE4NjE0Mn0.oXDl9yU5BoYdH1WpVbJWHyVs8w6Lu5F9AxUxJnFl8CE"


@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")

# --- TÍTULO DE LA APLICACIÓN WEB ---
st.title("🎓 Control de Alumnos - Panel Web")
st.markdown("Mantenimiento en tiempo real conectado a **Supabase**.")
st.divider()

# --- MENÚ LATERAL DE NAVEGACIÓN ---
opcion = st.sidebar.selectbox(
    "Selecciona una Operación CRUD",
    ["📁 Ver Alumnos (Read)", "➕ Registrar Nuevo (Create)", "🔄 Actualizar Datos (Update)", "❌ Eliminar Registro (Delete)"]
)

# ==========================================
# 1. READ: VER TODOS LOS ALUMNOS
# ==========================================
if opcion == "📁 Ver Alumnos (Read)":
    st.subheader("Lista Completa de Alumnos")
    
    try:
        response = supabase.table("ALUMNOS").select("*").order("APELLIDO_PAT").execute()
        if response.data:
            # Mostramos los datos en una tabla web interactiva nativa de Streamlit
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
                    st.error(f"No se pudo registrar. Verifique las restricciones (Ej: DNI único).\n\nDetalle: {e}")

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
                
                # Cargamos los datos actuales en el formulario web
                with st.form("form_actualizar"):
                    nuevo_pat = st.text_input("Apellido Paterno:", value=alumno.get("APELLIDO_PAT", ""))
                    nuevo_mat = st.text_input("Apellido Materno:", value=alumno.get("APELLIDO_MAT", "") or "")
                    nuevo_nom = st.text_input("Nombres:", value=alumno.get("NOMBRE", ""))
                    
                    # Buscamos el índice actual del sexo para dejarlo preseleccionado
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
                        st.success("¡Datos actualizados correctamente en la base de datos!")
            else:
                st.error("No se encontró ningún alumno con ese DNI.")
        except Exception as e:
            st.error(f"Error al buscar el alumno: {e}")

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
                
                # Casilla de confirmación obligatoria para la interfaz web
                confirmar = st.checkbox("Sí, confirmo que deseo borrar este registro de forma permanente.")
                btn_eliminar = st.button("Eliminar permanentemente", type="secondary")
                
                if btn_eliminar:
                    if confirmar:
                        supabase.table("ALUMNOS").delete().eq("DNI", dni_eliminar).execute()
                        st.success("El alumno ha sido borrado de la base de datos.")
                    else:
                        st.error("Debe marcar la casilla de confirmación antes de eliminar.")
            else:
                st.error("No se encontró ningún alumno con ese DNI.")
        except Exception as e:
            st.error(f"Error al procesar la baja: {e}")
