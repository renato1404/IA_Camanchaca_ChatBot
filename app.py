import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from clima_utils import (
    CENTROS,
    get_clima_actual as _get_c,
    get_pronostico_semana as _get_p,
    get_condiciones_marinas as _get_m,
    formatear_clima,
    formatear_pronostico,
    formatear_marino,
    dir_a_texto,
    validar_entrada,
    sanitizar_pii,
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

def _marino_func(centro: str) -> str:
    return formatear_marino(_get_m(centro))

get_clima_actual = StructuredTool.from_function(
    func=_clima_func,
    name="get_clima_actual",
    description="Obtiene el clima actual con temperatura, humedad, viento (velocidad y dirección), índice UV nivel y precipitación. Parámetro: ensenada, puelche o huito.",
)

get_pronostico_semana = StructuredTool.from_function(
    func=_pronos_func,
    name="get_pronostico_semana",
    description="Obtiene el pronóstico de 7 días con temperatura min/max, viento, lluvia, probabilidad de lluvia, dirección del viento dominante y horas de sol (salida/puesta). Parámetro: ensenada, puelche o huito.",
)

get_condiciones_marinas = StructuredTool.from_function(
    func=_marino_func,
    name="get_condiciones_marinas",
    description="Obtiene condiciones marinas: temperatura del agua superficial, altura y dirección de ola, período de ola, altura/dirección/período de swell. Parámetro: ensenada, puelche o huito.",
)

tools = [get_clima_actual, get_pronostico_semana, get_condiciones_marinas]

SYSTEM_PROMPT = (
    "Eres un asistente experto en monitoreo climático y oceanográfico para Salmones Camanchaca. "
    "Responde en español de forma clara y profesional. "
    "Centros disponibles: Ensenada (Piscicultura Petrohué), Puelche, Huito (San José). "
    "Tienes 3 herramientas: clima actual (temp, humedad, viento con dirección, UV con nivel, lluvia), "
    "pronóstico semanal (7 días, prob. lluvia, viento dominante, salida/puesta del sol), "
    "y condiciones marinas (temp. agua, altura/dirección/período de ola y swell). "
    "Usa la herramienta adecuada según la consulta."
)

if "agente" not in st.session_state:
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("GITHUB_TOKEN"),
        model="gpt-4o",
        temperature=0,
        request_timeout=600,
    )
    st.session_state.agente = create_react_agent(llm, tools)

EMOJIS = {"Despejado": "☀️", "Nublado": "☁️", "Lluvia": "🌧️"}
PAGINAS = ["Inicio", "ChatBot", "Centros"]
ICONOS = {"Inicio": "🏠", "ChatBot": "💬", "Centros": "📍"}

with st.sidebar:
    if os.path.exists("assets/logo-cc-web-celeste.png"):
        st.image("assets/logo-cc-web-celeste.png", width=160)
    else:
        st.markdown("# 🌊")
    st.markdown("**Salmones Camanchaca**  \nMonitoreo Climático y Marino")
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
    st.title("🌊 Monitoreo Climático y Marino")
    st.markdown("Sistema multi-agente para centros de cultivo de **Salmones Camanchaca** en la Región de Los Lagos.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Centros de Cultivo", "3", "Ensenada · Puelche · Huito")
    col2.metric("Herramientas IA", "3", "Clima · Pronóstico · Marino")
    col3.metric("Variables en vivo", "15+", "Atmósfera + océano + sol")

    with st.container(border=True):
        st.markdown("**🌊 Nuevo: Condiciones Marinas**")
        st.markdown("Altura de olas, dirección y período del oleaje, altura de swell, temperatura del agua superficial. Datos vía Open-Meteo Marine API.")

    with st.container(border=True):
        st.markdown("**🌡️ Más variables atmosféricas**")
        st.markdown("Humedad relativa, índice UV con nivel de riesgo, dirección del viento en formato cardinal (N/S/E/O), probabilidad de precipitación, horas de salida y puesta del sol.")

    with st.container(border=True):
        st.markdown("**📍 Centros de Cultivo**")
        st.markdown("**Piscicultura Petrohué** (Ensenada), **Centro Puelche** y **Centro Huito (San José)** en la Región de Los Lagos.")

    if st.button("💬 Ir al ChatBot", type="primary", use_container_width=True):
        st.session_state.pagina = "ChatBot"
        st.rerun()

elif page == "ChatBot":
    st.title("💬 ChatBot Climático y Marino")
    st.markdown("Pregunta por clima actual, pronóstico semanal o condiciones marinas de **Ensenada**, **Puelche** o **Huito**: temperatura, humedad, viento (velocidad y dirección), índice UV, lluvia, probabilidad de lluvia, salida/puesta del sol, altura y período de olas, swell, temperatura del agua.")

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ej: clima en Ensenada, pronóstico Puelche, condiciones marinas Huito..."):
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
                    historial = [("system", SYSTEM_PROMPT)]
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
    st.markdown("Datos atmosféricos y marinos en vivo de cada centro.")

    cols = st.columns(3)
    for i, (key, info) in enumerate(CENTROS.items()):
        with cols[i]:
            clima = _get_c(key)
            marino = _get_m(key)
            if "error" in clima:
                with st.container(border=True):
                    st.markdown(f"**{info['nombre']}**  \n{info['region']}")
                    st.markdown("Datos no disponibles")
            else:
                with st.container(border=True):
                    st.markdown(f"{EMOJIS.get(clima['condicion'], '❓')} **{info['nombre']}**  \n{info['region']}")
                    st.markdown(f"🌡️ **{clima['temp']}°C** — {clima['condicion']}")
                    if clima.get("humedad") is not None:
                        st.markdown(f"💧 Humedad: {clima['humedad']}%")
                    dir_txt = dir_a_texto(clima.get("viento_dir"))
                    v_str = f"{clima['viento']} km/h {dir_txt}" if dir_txt else f"{clima['viento']} km/h"
                    st.markdown(f"🌬️ Viento: {v_str}")
                    st.markdown(f"🌧️ Lluvia: {clima['lluvia']} mm")
                    if clima.get("uv") is not None:
                        nivel = "Bajo" if clima["uv"] < 3 else "Moderado" if clima["uv"] < 6 else "Alto" if clima["uv"] < 8 else "Muy alto"
                        st.markdown(f"☀️ UV: {clima['uv']} ({nivel})")
                    if "error" not in marino:
                        if marino.get("temp_agua") is not None:
                            st.markdown(f"🌡️ Agua: {marino['temp_agua']}°C")
                        if marino.get("ola_altura") is not None:
                            d = dir_a_texto(marino.get("ola_direccion"))
                            ola = f"{marino['ola_altura']} m" + (f" {d}" if d else "")
                            st.markdown(f"🌊 Ola: {ola} / {marino.get('ola_periodo','?')}s")
                        if marino.get("swell_altura") is not None:
                            d = dir_a_texto(marino.get("swell_direccion"))
                            sw = f"{marino['swell_altura']} m" + (f" {d}" if d else "")
                            st.markdown(f"📈 Swell: {sw} / {marino.get('swell_periodo','?')}s")
