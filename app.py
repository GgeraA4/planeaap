import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO

# Configuración
if "GENAI_KEY" in st.secrets:
    api_key = st.secrets["GENAI_KEY"]
else:
    api_key = "" 
if not api_key:
    st.error("No se encontró la configuración de la API Key.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')

st.set_page_config(page_title="Planeador Mágico", page_icon="🍎")

# --- FUNCIONES ---
def crear_word(titulo, contenido):
    doc = Document()
    doc.add_heading(f"Planeación: {titulo}", 0)
    # Limpiamos un poco el texto para el Word
    doc.add_paragraph(contenido.replace('#', '')) 
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- MEMORIA DE LA APP ---
# Si no existe la variable 'resultado' en la memoria, la creamos vacía
if 'resultado' not in st.session_state:
    st.session_state.resultado = None
if 'tema_guardado' not in st.session_state:
    st.session_state.tema_guardado = ""

st.title("🍎 Asistente para Maestras")

col1, col2 = st.columns(2)
with col1:
    tema = st.text_input("¿Qué tema vas a enseñar?", placeholder="Ej. Fracciones")
with col2:
    grado = st.selectbox("¿Para qué grado?", ["Preescolar", "1º Primaria", "2º Primaria", "3º Primaria", "4º Primaria", "5º Primaria", "6º Primaria", "Secundaria"])

boton_generar = st.button("Generar Planeación ✨", use_container_width=True)

# Lógica al presionar el botón de generar
if boton_generar:
    if tema:
        with st.spinner('Diseñando la clase...'):
            prompt = f"Actúa como experto pedagogo. Genera una planeación didáctica sobre '{tema}' para {grado}. Incluye Resumen, Objetivo y 3 actividades. Responde en español."
            response = model.generate_content(prompt)
            
            # GUARDAMOS EN LA MEMORIA
            st.session_state.resultado = response.text
            st.session_state.tema_guardado = tema
    else:
        st.warning("Escribe un tema primero.")

# --- MOSTRAR RESULTADOS SI EXISTEN EN MEMORIA ---
if st.session_state.resultado:
    st.divider()
    st.markdown(st.session_state.resultado)
    
    # El botón de descarga ahora usa la información guardada en memoria
    archivo_word = crear_word(st.session_state.tema_guardado, st.session_state.resultado)
    
    st.download_button(
        label="📥 Descargar planeación en Word",
        data=archivo_word,
        file_name=f"Planeacion_{st.session_state.tema_guardado}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )