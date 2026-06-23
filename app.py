import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from clima_utils import (
    CENTROS, get_clima_actual as _get_c, get_pronostico_semana as _get_p,
    formatear_clima, formatear_pronostico,
    validar_entrada, sanitizar_pii,
)

load_dotenv()

if not os.getenv("OPENAI_BASE_URL") or not os.getenv("GITHUB_TOKEN"):
    st.error("Falta OPENAI_BASE_URL o GITHUB_TOKEN en .env")
    st.stop()

st.set_page_config(page_title="Camanchaca — ChatBot Climático", page_icon="🌊", layout="wide")

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
def _clima_func(centro: str) -> str:
    return formatear_clima(_get_c(centro))

def _pronos_func(centro: str) -> str:
    return formatear_pronostico(_get_p(centro))

get_clima_actual = StructuredTool.from_function(
    func=_clima_func,
    name="get_clima_actual",
    description="Obtiene el clima actual. Parámetro: ensenada, puelche o huito.",
)

get_pronostico_semana = StructuredTool.from_function(
    func=_pronos_func,
    name="get_pronostico_semana",
    description="Obtiene el pronóstico de 7 días. Parámetro: ensenada, puelche o huito.",
)

if "agente" not in st.session_state:
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("GITHUB_TOKEN"),
        model="gpt-4o",
        temperature=0,
        request_timeout=600,
    )
    st.session_state.agente = create_react_agent(llm, [get_clima_actual, get_pronostico_semana])

EMOJIS = {"Despejado": "☀️", "Nublado": "☁️", "Lluvia": "🌧️"}
PAGINAS = ["Inicio", "ChatBot", "Centros"]
ICONOS = {"Inicio": "🏠", "ChatBot": "💬", "Centros": "📍"}

with st.sidebar:
    st.image("assets/logo-cc-web-celeste.png", width=160) if os.path.exists("assets/logo-cc-web-celeste.png") else st.markdown("# 🌊")
    st.markdown("**Salmones Camanchaca**  \nMonitoreo Climático")
    st.divider()
    for p in PAGINAS:
        if st.button(f"{ICONOS[p]} {p}", key=p, use_container_width=True,
                     type="primary" if st.session_state.pagina == p else "secondary"):
            st.session_state.pagina = p
            st.rerun()
    st.divider()
    st.caption("© 2026 — Ingeniería en IA  \nDuoc UC")

page = st.session_state.pagina

if page == "Inicio":
    st.title("🌊 Monitoreo Climático Inteligente")
    st.markdown("Asistente multi-agente para centros de cultivo de **Salmones Camanchaca** en la Región de Los Lagos.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Centros de Cultivo", "3", "Ensenada · Puelche · Huito")
    col2.metric("Herramientas IA", "2", "Clima · Pronóstico")
    col3.metric("Notebooks", "12", "IL1 · IL2 · IL3")

    with st.container(border=True):
        st.markdown("**📍 Centros de Cultivo**")
        st.markdown("El sistema monitorea las condiciones climáticas en tres centros de la Región de Los Lagos: **Piscicultura Petrohué** (Ensenada), **Centro Puelche** y **Centro Huito (San José)**. Cada centro cuenta con consultas en tiempo real de temperatura, viento, precipitación y condición meteorológica vía Open-Meteo API.")

    with st.container(border=True):
        st.markdown("**🤖 Arquitectura del Agente**")
        st.markdown("El chatbot utiliza un agente **ReAct (Reasoning + Acting)** implementado con LangGraph. El flujo sigue el ciclo: el LLM recibe la consulta → razona qué herramienta usar → invoca la API de Open-Meteo → observa el resultado → genera una respuesta clara. El historial conversacional se mantiene en memoria de sesión.")

    if st.button("💬 Ir al ChatBot", type="primary", use_container_width=True):
        st.session_state.pagina = "ChatBot"
        st.rerun()

elif page == "ChatBot":
    st.title("💬 ChatBot Climático")
    st.markdown("Consulta el clima en tiempo real para los centros de cultivo.")

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Pregunta por el clima en Ensenada, Puelche o Huito..."):
        ok, err = validar_entrada(prompt)
        if not ok:
            st.warning(err)
            st.stop()
        prompt = sanitizar_pii(prompt)

        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando..."):
                try:
                    historial = [("system", "Eres un asistente experto en monitoreo climático para Salmones Camanchaca. Responde en español de forma clara. Centros: Ensenada (Piscicultura Petrohué), Puelche, Huito.")]
                    for m in st.session_state.mensajes[-6:]:
                        historial.append(("human" if m["role"] == "user" else "ai", m["content"]))
                    resp = st.session_state.agente.invoke({"messages": historial})
                    contenido = resp["messages"][-1].content
                    st.write(contenido)
                    st.session_state.mensajes.append({"role": "assistant", "content": contenido})
                except Exception as e:
                    st.error(f"Error: {e}")

elif page == "Centros":
    st.title("📍 Centros de Cultivo")
    st.markdown("Información y clima en vivo de cada centro.")

    cols = st.columns(3)
    for i, (key, info) in enumerate(CENTROS.items()):
        with cols[i]:
            datos = _get_c(key)
            if "error" in datos:
                with st.container(border=True):
                    st.markdown(f"**{info['nombre']}**  \n{info['region']}")
                    st.markdown("Datos no disponibles")
            else:
                with st.container(border=True):
                    st.markdown(f"{EMOJIS.get(datos['condicion'], '❓')} **{info['nombre']}**  \n{info['region']}")
                    st.markdown(f"**Temperatura:** {datos['temp']}°C")
                    st.markdown(f"**Viento:** {datos['viento']} km/h")
                    st.markdown(f"**Precipitación:** {datos['lluvia']} mm")
                    st.markdown(f"**Condición:** {datos['condicion']}")


