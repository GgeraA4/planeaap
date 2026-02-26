import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt
from io import BytesIO

# --- CONFIGURACIÓN DE LA API ---
if "GENAI_KEY" in st.secrets:
    api_key = st.secrets["GENAI_KEY"]
else:
    api_key = "" 

if not api_key:
    st.error("No se encontró la configuración de la API Key.")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-3-flash-preview')

st.set_page_config(page_title="Asistente Planeador", page_icon="🍎", layout="wide")

# --- FUNCIONES ---
def crear_word(titulo, contenido):
    doc = Document()
    doc.add_heading(f"Planeación: {titulo}", 0)
    
    # Procesamos el texto línea por línea para dar formato
    lineas = contenido.split('\n')
    for linea in lineas:
        if linea.strip().startswith('#'):
            # Es un título: quitamos los # y lo hacemos grande y negrita
            texto_limpio = linea.replace('#', '').strip()
            p = doc.add_paragraph()
            run = p.add_run(texto_limpio)
            run.bold = True
            run.font.size = Pt(14)
        else:
            # Es texto normal (también limpiamos asteriscos dobles si quieres)
            texto_limpio = linea.replace('**', '') 
            doc.add_paragraph(texto_limpio)
            
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- MEMORIA DE LA APP ---
if 'resultado' not in st.session_state:
    st.session_state.resultado = None
if 'tema_guardado' not in st.session_state:
    st.session_state.tema_guardado = ""

# --- BARRA LATERAL (SIMULACIÓN DE HISTORIAL DE USUARIO) ---
with st.sidebar:
    st.header("👤 Mi Perfil")
    st.write("Bienvenida, Maestra.")
    st.divider()
    st.subheader("📚 Mis Planeaciones Guardadas")
    st.info("Aquí aparecerá tu historial cuando conectemos la base de datos (Supabase). Podrás dar clic para verlas o eliminarlas.")
    # Ejemplo visual de cómo se verá:
    st.button("📄 Fracciones (4º Primaria)")
    st.button("📄 Ciclo del Agua (3º Primaria)")

# --- INTERFAZ PRINCIPAL ---
st.title("🍎 Asistente de Planeaciones 📚")

# CONTENEDOR 1: Datos principales de la clase
with st.container(border=True):
    st.subheader("1. Datos de la Clase")
    col1, col2 = st.columns(2)
    with col1:
        tema = st.text_input("¿Qué tema vas a enseñar?", placeholder="Ej. Fracciones equivalentes")
    with col2:
        grado = st.selectbox("¿Para qué grado?", ["Preescolar", "1º Primaria", "2º Primaria", "3º Primaria", "4º Primaria", "5º Primaria", "6º Primaria", "Secundaria"])
    
    metodologias = [
        "Constructivismo", 
        "Aprendizaje Basado en Proyectos (ABP)", 
        "Aprendizaje Basado en Problemas", 
        "Enfoque por Competencias", 
        "Aula Invertida (Flipped Classroom)",
        "Sistema Preventivo (Escuelas Salesianas)"
    ]
    metodologia = st.selectbox("¿Qué metodología o enfoque deseas utilizar?", metodologias)

# CONTENEDOR 2: Opciones adicionales (Desplegable)
with st.expander("🛠️ 2. Opciones Adicionales (Opcional)"):
    st.write("Selecciona si deseas incluir material extra en tu planeación:")
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        incluir_quiz = st.checkbox("Añadir un Quiz rápido")
    with col_opt2:
        incluir_examen = st.checkbox("Sugerencia de preguntas de examen")
    with col_opt3:
        incluir_proyecto = st.checkbox("Proyecto mensual relacionado")

boton_generar = st.button("Generar Planeación ✨", use_container_width=True, type="primary")

# --- LÓGICA AL PRESIONAR EL BOTÓN ---
if boton_generar:
    if tema:
        with st.spinner('Diseñando la clase mágica...'):
            # Construimos las instrucciones extra basadas en los checkboxes
            instrucciones_extra = ""
            if incluir_quiz:
                instrucciones_extra += " - Incluye un quiz rápido de 5 preguntas para evaluar la comprensión inmediata.\n"
            if incluir_examen:
                instrucciones_extra += " - Sugiere 5 preguntas de opción múltiple tipo examen con sus respuestas.\n"
            if incluir_proyecto:
                instrucciones_extra += " - Propón una idea para un proyecto mensual relacionado con este tema.\n"

            # Construimos el prompt final integrando la metodología
            prompt = (f"Actúa como experto pedagogo. Genera una planeación didáctica sobre '{tema}' para {grado}. "
                    f"Es FUNDAMENTAL que bases toda la planeación y el tono en la metodología: {metodologia}. "
                    f"Incluye Resumen, Objetivo y 3 actividades con el tiempo estimado de cada una. "
                    f"Añade actividades complementarias (hojas lúdicas) e incluye fuentes de apoyo (libros, citas en linea, etc.). "
                    f"Incluye algunos links a videos de apoyo en YouTube. Responde en español.\n"
                    f"Además, incluye lo siguiente:\n{instrucciones_extra}"
                    f"No aclares en el texto que eres un experto pedagogo.")
            
            response = model.generate_content(prompt)
            
            # GUARDAMOS EN LA MEMORIA
            st.session_state.resultado = response.text
            st.session_state.tema_guardado = tema
    else:
        st.warning("Escribe un tema primero.")

# --- MOSTRAR RESULTADOS ---
if st.session_state.resultado:
    st.divider()
    st.success(f"Aquí tienes tu planeación basada en **{metodologia}**")
    
    with st.container(border=True):
        st.markdown(st.session_state.resultado)
    
    # El botón de descarga ahora usa la información guardada en memoria
    archivo_word = crear_word(st.session_state.tema_guardado, st.session_state.resultado)
    
    st.download_button(
        label="📥 Descargar planeación en Word",
        data=archivo_word,
        file_name=f"Planeacion_{st.session_state.tema_guardado}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    )
