import os
import re
import json
import time
import requests
from typing import List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import streamlit as st

load_dotenv()

st.set_page_config(
    page_title="IA Camanchaca — AI Operations Suite",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Hanken+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,0&display=swap" rel="stylesheet">
<style>
    :root {
        --color-primary: #005596;
        --color-primary-dark: #003e6f;
        --color-primary-container: #d3e4ff;
        --color-secondary: #006688;
        --color-secondary-container: #43c5fd;
        --color-accent: #00A9E0;
        --color-surface: #fbf9f8;
        --color-surface-container: #f5f3f3;
        --color-surface-high: #eae8e7;
        --color-surface-highest: #e4e2e2;
        --color-outline: #727781;
        --color-outline-variant: #c1c7d2;
        --color-error: #ba1a1a;
        --color-success: #1e7e34;
        --color-warning: #b9770e;
        --color-white: #ffffff;
        --color-on-surface: #1b1c1c;
        --color-on-surface-variant: #414750;
        --font-heading: 'Hanken Grotesk', sans-serif;
        --font-body: 'Inter', sans-serif;
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --shadow-card: 0px 2px 4px rgba(0, 85, 150, 0.05);
        --shadow-hover: 0px 4px 12px rgba(0, 85, 150, 0.1);
        --space-base: 8px;
        --space-gutter: 24px;
    }

    #root > div:first-child {
        background: var(--color-surface);
    }

    .stApp {
        background: var(--color-surface);
    }

    section[data-testid="stSidebar"] {
        background: var(--color-primary-dark) !important;
        border-right: none;
        min-width: 260px !important;
    }

    section[data-testid="stSidebar"] .st-emotion-cache-1gv3huu {
        background: var(--color-primary-dark);
    }

    section[data-testid="stSidebar"] .sidebar-content {
        padding: 0;
    }

    .sidebar-logo {
        padding: 24px 20px 16px;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 8px;
    }

    .sidebar-logo img {
        max-width: 180px;
        margin-bottom: 12px;
    }

    .sidebar-logo h1 {
        font-family: var(--font-heading);
        font-size: 20px;
        font-weight: 700;
        color: var(--color-white);
        margin: 0;
        line-height: 1.3;
    }

    .sidebar-logo p {
        font-family: var(--font-body);
        font-size: 11px;
        font-weight: 600;
        color: rgba(255,255,255,0.6);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 4px 0 0;
    }

    .stSidebar .stRadio {
        padding: 4px 8px;
    }

    .stSidebar .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .stSidebar .stRadio label {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 10px 14px !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        color: rgba(255,255,255,0.75) !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    .stSidebar .stRadio label:hover {
        background: rgba(255,255,255,0.08) !important;
        color: var(--color-white) !important;
    }

    .stSidebar .stRadio label[data-selected="true"] {
        background: var(--color-primary) !important;
        color: var(--color-white) !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-card);
    }

    .stSidebar .stRadio label[data-selected="true"] .nav-icon {
        color: var(--color-white) !important;
    }

    .nav-icon {
        font-family: 'Material Symbols Outlined';
        font-size: 20px;
        width: 24px;
        text-align: center;
        color: rgba(255,255,255,0.5);
        transition: color 0.2s;
    }

    .stSidebar .stRadio label:hover .nav-icon {
        color: var(--color-white);
    }

    .stSidebar .stRadio label[data-selected="true"] .nav-icon {
        color: var(--color-white) !important;
    }

    .sidebar-footer {
        position: absolute;
        bottom: 16px;
        left: 0;
        right: 0;
        padding: 16px 20px;
        border-top: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }

    .sidebar-footer p {
        font-family: var(--font-body);
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        margin: 0;
        letter-spacing: 0.03em;
    }

    .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak {
        background-color: transparent !important;
    }

    .main-header {
        font-family: var(--font-heading);
        font-size: 32px;
        font-weight: 700;
        color: var(--color-primary-dark);
        margin-bottom: 4px;
        line-height: 1.2;
    }

    .sub-header {
        font-family: var(--font-body);
        font-size: 16px;
        font-weight: 400;
        color: var(--color-on-surface-variant);
        margin-top: 0;
        margin-bottom: 24px;
    }

    .glass-card {
        background: var(--color-white);
        border: 1px solid var(--color-outline-variant);
        border-radius: var(--radius-lg);
        padding: 20px 24px;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        margin-bottom: 16px;
    }

    .glass-card:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }

    .glass-card h3 {
        font-family: var(--font-heading);
        font-size: 18px;
        font-weight: 600;
        color: var(--color-primary);
        margin: 0 0 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .glass-card p {
        font-family: var(--font-body);
        font-size: 14px;
        color: var(--color-on-surface-variant);
        line-height: 1.6;
        margin: 0;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 20px;
        font-family: var(--font-body);
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.03em;
    }

    .badge-ok {
        background: #e6f4ea;
        color: var(--color-success);
    }

    .badge-warn {
        background: #fef7e0;
        color: #b9770e;
    }

    .badge-info {
        background: #e8f0fe;
        color: var(--color-primary);
    }

    .badge-error {
        background: #fce8e6;
        color: var(--color-error);
    }

    .metric-card {
        background: var(--color-white);
        border: 1px solid var(--color-outline-variant);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        text-align: center;
    }

    .metric-card:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }

    .metric-card .metric-value {
        font-family: var(--font-heading);
        font-size: 28px;
        font-weight: 700;
        color: var(--color-primary-dark);
        line-height: 1.2;
    }

    .metric-card .metric-label {
        font-family: var(--font-body);
        font-size: 12px;
        font-weight: 600;
        color: var(--color-outline);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    .metric-card .metric-delta {
        font-family: var(--font-body);
        font-size: 12px;
        font-weight: 400;
        color: var(--color-outline);
        margin-top: 2px;
    }

    .stButton > button {
        font-family: var(--font-body) !important;
        font-weight: 600 !important;
        border-radius: var(--radius-md) !important;
        padding: 8px 20px !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }

    .stButton > button[kind="primary"] {
        background: var(--color-primary) !important;
        color: var(--color-white) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--color-primary-dark) !important;
        box-shadow: var(--shadow-hover) !important;
    }

    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: var(--color-primary) !important;
        border: 1.5px solid var(--color-primary) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(0, 85, 150, 0.05) !important;
    }

    .chat-message-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
    }

    .chat-message-user > div {
        background: var(--color-surface-high);
        color: var(--color-on-surface);
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        font-family: var(--font-body);
        font-size: 14px;
        line-height: 1.5;
        box-shadow: var(--shadow-card);
    }

    .chat-message-ai {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 16px;
        gap: 12px;
    }

    .chat-message-ai .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--color-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: var(--shadow-card);
    }

    .chat-message-ai .avatar span {
        color: var(--color-white);
        font-size: 18px;
    }

    .chat-message-ai .bubble {
        background: var(--color-white);
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        max-width: 70%;
        font-family: var(--font-body);
        font-size: 14px;
        line-height: 1.5;
        color: var(--color-on-surface);
        box-shadow: var(--shadow-card);
        border: 1px solid var(--color-outline-variant);
    }

    div[data-testid="stChatInput"] {
        border: 1.5px solid var(--color-outline-variant) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--color-white) !important;
        box-shadow: var(--shadow-card) !important;
        padding: 4px !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 85, 150, 0.1) !important;
    }

    div[data-testid="stChatInput"] input {
        font-family: var(--font-body) !important;
        font-size: 14px !important;
    }

    .stInfo {
        background: #e8f0fe !important;
        border: 1px solid #c5d9f2 !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
        font-size: 13px !important;
        color: var(--color-on-surface-variant) !important;
    }

    .stAlert {
        border-radius: var(--radius-md) !important;
        font-family: var(--font-body) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-heading) !important;
        color: var(--color-primary-dark) !important;
    }

    p, li, .stMarkdown {
        font-family: var(--font-body) !important;
        color: var(--color-on-surface) !important;
    }

    code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
        font-size: 13px !important;
    }

    hr {
        border-color: var(--color-outline-variant) !important;
        margin: 24px 0 !important;
        opacity: 0.5;
    }

    .section-title {
        font-family: var(--font-heading);
        font-size: 14px;
        font-weight: 600;
        color: var(--color-secondary);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    [data-testid="column"] {
        gap: 16px !important;
    }

    .st-emotion-cache-1r6slb0 {
        gap: 16px;
    }

    .notebook-card {
        background: var(--color-white);
        border: 1px solid var(--color-outline-variant);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        box-shadow: var(--shadow-card);
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }

    .notebook-card:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-1px);
    }

    .notebook-card .nb-title {
        font-family: var(--font-heading);
        font-size: 16px;
        font-weight: 600;
        color: var(--color-primary-dark);
    }

    .notebook-card .nb-section {
        font-family: var(--font-body);
        font-size: 11px;
        font-weight: 600;
        color: var(--color-secondary);
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .notebook-card .nb-desc {
        font-family: var(--font-body);
        font-size: 14px;
        font-weight: 600;
        color: var(--color-on-surface);
        margin: 4px 0;
    }

    .notebook-card .nb-detail {
        font-family: var(--font-body);
        font-size: 13px;
        color: var(--color-on-surface-variant);
        line-height: 1.5;
    }

    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--color-outline-variant);
        border-radius: 10px;
    }

    .st-emotion-cache-1gwvy38 {
        display: none;
    }

    .element-container:has(> div > div > .stSidebarNavItems) {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

if os.path.exists("assets/logo-cc-web-celeste.png"):
    st.sidebar.image("assets/logo-cc-web-celeste.png", width=180)

st.sidebar.markdown("""
<div class="sidebar-logo">
    <h1>Salmones Camanchaca</h1>
    <p>AI Operations Suite</p>
</div>
""", unsafe_allow_html=True)

pagina = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Chatbot", "Notebooks", "Arquitectura", "Observabilidad", "Seguridad", "Despliegue"],
    label_visibility="collapsed",
)

st.sidebar.markdown("""
<div class="sidebar-footer">
    <p>Camanchaca © 2025<br>AI-Driven Aquaculture</p>
</div>
""", unsafe_allow_html=True)

def encabezado_seccion(titulo, subtitulo=None, icono=None):
    icono_html = f"<span class='material-symbols-outlined' style='font-size:32px;color:var(--color-primary);vertical-align:middle;margin-right:8px'>{icono}</span>" if icono else ""
    st.markdown(f"<p class='section-title'>{subtitulo or ''}</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='main-header'>{icono_html}{titulo}</h1>", unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f"<p class='sub-header'>{subtitulo}</p>", unsafe_allow_html=True)

if pagina == "Inicio":
    encabezado_seccion("Sistema de Agentes Camanchaca", "MONITOREO CLIMÁTICO Y OPERACIONAL")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3><span class="material-symbols-outlined" style="font-size:20px">description</span> Resumen del Proyecto</h3>
            <p>Sistema multi-agente para <strong>Salmones Camanchaca</strong> que automatiza el monitoreo de
            condiciones climáticas en centros de cultivo de la Región de Los Lagos
            (<strong>Ensenada, Puelche y Huito</strong>). Los agentes consultan APIs externas,
            mantienen memoria conversacional y aplican RAG para fundamentar decisiones operativas.</p>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">12</div>
                <div class="metric-label">Notebooks</div>
                <div class="metric-delta">IA, CoT, RAG, Agentes</div>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">4</div>
                <div class="metric-label">Herramientas</div>
                <div class="metric-delta">Clima, Pronóstico, Evaluación, Mejor Día</div>
            </div>
            """, unsafe_allow_html=True)
        with col_c:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">3</div>
                <div class="metric-label">Centros</div>
                <div class="metric-delta">Ensenada, Puelche, Huito</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if os.path.exists("dashboard_observabilidad_camanchaca.png"):
            st.image("dashboard_observabilidad_camanchaca.png", caption="Dashboard de Observabilidad", use_container_width=True)
        else:
            st.markdown("""
            <div class="glass-card">
                <h3><span class="material-symbols-outlined" style="font-size:20px">info</span> Dashboard</h3>
                <p>Ejecuta <code>IA_agente_Camanchaca5.ipynb</code> para generar el dashboard de observabilidad.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h2 style='font-family:var(--font-heading);font-size:22px;font-weight:600;color:var(--color-primary-dark)'>🧱 Stack Tecnológico</h2>", unsafe_allow_html=True)
    cols = st.columns(5)
    stacks = [("Python 3.11", "🐍"), ("LangChain", "⛓️"), ("LangGraph", "🕸️"), ("CrewAI", "🤖"), ("OpenAI/GitHub Models", "🧠")]
    for i, (name, icon) in enumerate(stacks):
        cols[i].markdown(f"""
        <div class="glass-card" style="text-align:center;padding:16px">
            <div style="font-size:32px;margin-bottom:8px">{icon}</div>
            <div style="font-family:var(--font-body);font-size:13px;font-weight:600;color:var(--color-primary-dark)">{name}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h2 style='font-family:var(--font-heading);font-size:22px;font-weight:600;color:var(--color-primary-dark)'>📂 Estructura del Proyecto</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="glass-card">
        <pre style="font-size:13px;line-height:1.6;color:var(--color-on-surface-variant);margin:0;background:var(--color-surface-container);padding:16px;border-radius:var(--radius-md);overflow-x:auto">
IA_Camanchaca_ChatBot/
├── IA_Camanchaca.ipynb          # Chatbot base con memoria
├── IA_Camanchaca2.ipynb         # Chain-of-Thought + Few-Shot
├── IA_Camanchaca3.ipynb         # RAG con FAISS vector store
├── IA_agente_Camanchaca1.ipynb  # Agente ReAct + Function Calling + CrewAI
├── IA_agente_Camanchaca2.ipynb  # Memoria: Buffer, Window y Summary
├── IA_agente_Camanchaca3.ipynb  # Planificación y orquestación
├── IA_agente_Camanchaca4.ipynb  # Arquitectura y buenas prácticas
├── IA_agente_Camanchaca5.ipynb  # Observabilidad y métricas (IL3.1)
├── IA_agente_Camanchaca6.ipynb  # Trazabilidad y logs (IL3.2)
├── IA_agente_Camanchaca7.ipynb  # Seguridad y ética (IL3.3)
├── IA_agente_Camanchaca8.ipynb  # Escalabilidad y sostenibilidad (IL3.4)
├── IA_agente_Camanchaca9.ipynb  # Ciberseguridad y despliegue AWS (IL3.5)
├── bot.py
├── app.py                       # Esta aplicación Streamlit
├── requirements.txt
└── .env
        </pre>
        </div>
        """, unsafe_allow_html=True)

elif pagina == "Chatbot":
    encabezado_seccion("Chatbot Camanchaca", "CONSULTA CLIMÁTICA Y OPERATIVA", "smart_toy")

    st.markdown("""
    <div class="glass-card" style="background:var(--color-surface-container)">
        <div style="display:flex;gap:12px;flex-wrap:wrap">
            <span class="badge badge-info">💡 Pronóstico 7 días</span>
            <span class="badge badge-info">🌡️ Clima actual</span>
            <span class="badge badge-info">🌊 Estado de centros</span>
            <span class="badge badge-info">⚠️ Alertas climáticas</span>
        </div>
        <p style="margin-top:8px;font-size:13px"><strong>Ejemplos:</strong> "¿Cuál es el clima actual en Ensenada?" • "¿Cómo viene el pronóstico semanal para Puelche?" • "¿Hay alertas climáticas en Huito?"</p>
    </div>
    """, unsafe_allow_html=True)

    CENTROS = {
        "ensenada": {"lat": -41.140459, "lon": -72.404236, "nombre": "Piscicultura Petrohué"},
        "puelche":  {"lat": -41.733,    "lon": -73.602,    "nombre": "Centro Puelche"},
        "huito":    {"lat": -41.783,    "lon": -73.583,    "nombre": "Centro Huito (San José)"},
    }

    @tool
    def get_clima_actual(centro: str) -> str:
        if centro.lower() not in CENTROS:
            return f"Centro '{centro}' no encontrado. Opciones: ensenada, puelche, huito."
        datos = CENTROS[centro.lower()]
        url = (f"https://api.open-meteo.com/v1/forecast"
               f"?latitude={datos['lat']}&longitude={datos['lon']}"
               f"&current=temperature_2m,wind_speed_10m,precipitation,weathercode"
               f"&timezone=America/Santiago")
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            current = data["current"]
            temp = current["temperature_2m"]
            viento = current["wind_speed_10m"]
            lluvia = current["precipitation"]
            codigo = current["weathercode"]
            condicion = "Despejado" if codigo < 3 else "Nublado" if codigo < 50 else "Lluvia"
            return (f"Centro: {datos['nombre']}\nTemperatura: {temp}°C\n"
                    f"Viento: {viento} km/h\nPrecipitación: {lluvia} mm\nCondición: {condicion}")
        except Exception as e:
            return f"Error al obtener datos: {e}"

    @tool
    def get_pronostico_semana(centro: str) -> str:
        if centro.lower() not in CENTROS:
            return f"Centro '{centro}' no encontrado."
        datos = CENTROS[centro.lower()]
        url = (f"https://api.open-meteo.com/v1/forecast"
               f"?latitude={datos['lat']}&longitude={datos['lon']}"
               f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weathercode"
               f"&timezone=America/Santiago")
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            daily = data["daily"]
            resultado = f"Pronóstico 7 días - {datos['nombre']}:\n"
            for i in range(7):
                fecha = daily["time"][i]
                tmax = daily["temperature_2m_max"][i]
                tmin = daily["temperature_2m_min"][i]
                lluvia = daily["precipitation_sum"][i]
                viento = daily["wind_speed_10m_max"][i]
                codigo = daily["weathercode"][i]
                condicion = "Despejado" if codigo < 3 else "Nublado" if codigo < 50 else "Lluvia"
                resultado += f"\n{fecha}: {tmin}°C-{tmax}°C | Viento: {viento} km/h | Lluvia: {lluvia} mm | {condicion}"
            return resultado
        except Exception as e:
            return f"Error: {e}"

    tools_agente = [get_clima_actual, get_pronostico_semana]
    agente_llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("GITHUB_TOKEN"),
        model="gpt-4o",
        temperature=0,
        timeout=600,
    )
    agent_executor = create_react_agent(agente_llm, tools_agente)

    PATRONES_INJECTION = [
        r"ignora(?:r)?\s+(?:las\s+)?instrucciones", r"olvida(?:r)?\s+tus\s+instrucciones",
        r"eres\s+ahora\s+un", r"revela\s+tu\s+system\s*prompt",
        r"actua\s+como\s+si\s+no\s+tuvieras\s+reglas", r"sin\s+restricciones",
        r"bypassea(?:r)?\s+las?\s+seguridad", r"ignora\s+todas?\s+las?\s+reglas",
    ]
    PATRONES_PII = {
        "correo": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        "telefono": re.compile(r"(?:\+56\s?)?(?:9\s?\d{4}\s?\d{4}|\d{2}\s?\d{3}\s?\d{4})"),
        "rut": re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK]\b"),
    }

    def validar_entrada(texto):
        if not texto or not texto.strip():
            return False, "Entrada vacía."
        for patron in PATRONES_INJECTION:
            if re.search(patron, texto.lower()):
                return False, "Intento de prompt injection detectado."
        return True, ""

    def sanitizar_pii(texto):
        for tipo, patron in PATRONES_PII.items():
            texto = patron.sub(f"[{tipo.upper()}_REDACTADO]", texto)
        return texto

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
        st.session_state.historial = []

    for msg in st.session_state.mensajes:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message-user">
                <div>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message-ai">
                <div class="avatar"><span class="material-symbols-outlined">smart_toy</span></div>
                <div class="bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

    if prompt := st.chat_input("Describe una consulta o solicita un reporte..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        st.markdown(f"""
        <div class="chat-message-user">
            <div>{prompt}</div>
        </div>
        """, unsafe_allow_html=True)

        valida, motivo = validar_entrada(prompt)
        if not valida:
            respuesta = f"🚫 {motivo}"
            st.markdown(f"""
            <div class="chat-message-ai">
                <div class="avatar"><span class="material-symbols-outlined">smart_toy</span></div>
                <div class="bubble">{respuesta}</div>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        else:
            prompt_limpio = sanitizar_pii(prompt)
            st.session_state.historial.append(("human", prompt_limpio))
            historial_para_agente = st.session_state.historial[-6:]

            with st.spinner("Consultando agente Camanchaca..."):
                try:
                    response = agent_executor.invoke({"messages": historial_para_agente})
                    respuesta = response["messages"][-1].content
                    respuesta = sanitizar_pii(respuesta)
                except Exception as e:
                    respuesta = "Error al procesar la consulta."
            st.markdown(f"""
            <div class="chat-message-ai">
                <div class="avatar"><span class="material-symbols-outlined">smart_toy</span></div>
                <div class="bubble">{respuesta}</div>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
            st.session_state.historial.append(("ai", respuesta))

elif pagina == "Notebooks":
    encabezado_seccion("Explorador de Notebooks", "12 NOTEBOOKS — LÍNEAS DE APRENDIZAJE IL1 A IL3", "book")

    notebooks = [
        ("IL1.1-IL1.4", "IA_Camanchaca.ipynb", "Chatbot base con LangChain", "✅", "Chatbot conversacional con streaming, memoria de sesión y system prompt para acuicultura."),
        ("IL2.1", "IA_Camanchaca2.ipynb", "Chain-of-Thought + Few-Shot", "✅", "Razonamiento estructurado paso a paso con ejemplos few-shot para mortalidad, FCR y biometrías."),
        ("IL2.2", "IA_Camanchaca3.ipynb", "RAG con FAISS", "✅", "Retrieval-Augmented Generation usando FAISS como vector store."),
        ("IL2.3", "IA_agente_Camanchaca1.ipynb", "Agente ReAct + Function Calling + CrewAI", "✅", "Ciclo ReAct, Function Calling y multi-agente con CrewAI."),
        ("IL2.4", "IA_agente_Camanchaca2.ipynb", "Memoria (Buffer, Window, Summary)", "✅", "Tres estrategias de memoria conversacional comparadas."),
        ("IL2.5", "IA_agente_Camanchaca3.ipynb", "Planificación y Orquestación", "✅", "Planificación jerárquica, reactiva y por objetivos."),
        ("IL2.6", "IA_agente_Camanchaca4.ipynb", "Arquitectura y Buenas Prácticas", "✅", "Arquitectura en capas, configuración centralizada, DRY, pruebas unitarias."),
        ("IL3.1", "IA_agente_Camanchaca5.ipynb", "Observabilidad y Métricas (IE9)", "✅", "Logging estructurado, métricas de latencia, precisión y consistencia."),
        ("IL3.2", "IA_agente_Camanchaca6.ipynb", "Trazabilidad y Logs (IE10)", "✅", "Trace IDs únicos, trazas JSON, analizador de puntos de falla."),
        ("IL3.3", "IA_agente_Camanchaca7.ipynb", "Seguridad y Ética (IE11)", "✅", "Anti-prompt injection, PII, filtro ético, rate limiting."),
        ("IL3.4", "IA_agente_Camanchaca8.ipynb", "Escalabilidad y Sostenibilidad (IE12)", "✅", "CacheLLM, enrutamiento de modelos, procesamiento por lotes."),
        ("IL3.5", "IA_agente_Camanchaca9.ipynb", "Ciberseguridad y Despliegue AWS", "✅", "Guardrails, OWASP LLM Top 10, EC2 + Caddy + Docker."),
    ]

    for seccion, nombre, desc, estado, detalle in notebooks:
        st.markdown(f"""
        <div class="notebook-card">
            <div style="display:flex;justify-content:space-between;align-items:start">
                <div>
                    <span class="nb-section">{seccion}</span>
                    <div class="nb-title">{nombre}</div>
                </div>
                <span class="badge badge-ok">{estado}</span>
            </div>
            <div class="nb-desc">{desc}</div>
            <div class="nb-detail">{detalle}</div>
        </div>
        """, unsafe_allow_html=True)

elif pagina == "Arquitectura":
    encabezado_seccion("Arquitectura del Sistema", "CAPAS, COMPONENTES Y FLUJO DE DATOS", "account_tree")

    st.markdown("""
    <div class="glass-card">
        <h3><span class="material-symbols-outlined" style="font-size:20px">account_tree</span> Diagrama de Arquitectura</h3>
        <pre style="font-size:12px;line-height:1.5;color:var(--color-on-surface-variant);margin:0;background:var(--color-surface-container);padding:16px;border-radius:var(--radius-md);overflow-x:auto">
┌─────────────────────────────────────────────────────────────────┐
│                    OPERADOR CAMANCHACA                           │
│              (Consulta en lenguaje natural)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAPA DE PRESENTACIÓN (Streamlit / Jupyter)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAPA DE APLICACIÓN — AGENTES                        │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────────┐   │
│  │  Agente ReAct │  │  Memoria de    │  │  Crew Multi-Agente │   │
│  │  (LangGraph)  │  │  Sesión        │  │  (CrewAI)          │   │
│  └──────┬───────┘  └───────┬────────┘  └─────────┬──────────┘   │
│         └──────────────────┴──────────────────────┘              │
│                              ▼                                   │
│              ┌────────────────────────────┐                      │
│              │  Gestor de Herramientas     │                      │
│              └────────────────────────────┘                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAPA DE DOMINIO — HERRAMIENTAS                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ get_clima_   │  │get_pronostico│  │ evaluar_operacion    │   │
│  │ actual       │  │_semana       │  │                      │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         ▼                 ▼                      ▼               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              API Open-Meteo (gratuita, sin key)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FAISS Vector Store (RAG)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAPA DE INFRAESTRUCTURA                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   GitHub     │  │   LangSmith  │  │  AWS EC2 (Caddy +    │   │
│  │ Models API   │  │   Tracing    │  │  Docker)             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
        </pre>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='font-family:var(--font-heading);font-size:20px;font-weight:600;color:var(--color-primary-dark);margin-top:24px'>🧠 Componentes Clave</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3><span class="material-symbols-outlined" style="font-size:20px">sync_alt</span> LangGraph (ReAct)</h3>
            <p>• Ciclo <strong>Razonar → Actuar → Observar</strong><br>
            • Nativo en LangChain 1.3+<br>
            • Manejo de herramientas con @tool decorator</p>
        </div>
        <div class="glass-card">
            <h3><span class="material-symbols-outlined" style="font-size:20px">groups</span> CrewAI (Multi-Agente)</h3>
            <p>• <strong>Meteorólogo Acuícola</strong>: clima y pronóstico<br>
            • <strong>Coordinador Operaciones</strong>: planificación<br>
            • <strong>Supervisor General</strong>: reporte ejecutivo</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3><span class="material-symbols-outlined" style="font-size:20px">memory</span> Memoria Conversacional</h3>
            <p>• <code>InMemoryChatMessageHistory</code>: sesiones<br>
            • <code>ConversationBufferMemory</code>: historial completo<br>
            • <code>ConversationWindowMemory</code>: ventana k=2<br>
            • <code>ConversationSummaryMemory</code>: resumen automático</p>
        </div>
        <div class="glass-card">
            <h3><span class="material-symbols-outlined" style="font-size:20px">database</span> RAG con FAISS</h3>
            <p>• Embeddings: <code>text-embedding-3-small</code><br>
            • Chunk size: 400, overlap: 60<br>
            • Retrieve: top-k=2 por consulta</p>
        </div>
        """, unsafe_allow_html=True)

elif pagina == "Observabilidad":
    encabezado_seccion("Observabilidad y Métricas", "IL3.1 / IE9 — PRECISIÓN, LATENCIA Y CONSISTENCIA", "monitoring")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">4,253 ms</div>
            <div class="metric-label">Latencia Promedio</div>
            <div class="metric-delta">±10.75% CV</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">80%</div>
            <div class="metric-label">Precisión</div>
            <div class="metric-delta">Resp. con datos numéricos</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">100%</div>
            <div class="metric-label">Tasa de Éxito</div>
            <div class="metric-delta">Sin errores en 5 consultas</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">302</div>
            <div class="metric-label">Tokens Totales</div>
            <div class="metric-delta">5 consultas de prueba</div>
        </div>
        """, unsafe_allow_html=True)

    if os.path.exists("dashboard_observabilidad_camanchaca.png"):
        st.image("dashboard_observabilidad_camanchaca.png", caption="Dashboard de Observabilidad — Latencia y Precisión por Consulta", use_container_width=True)
    else:
        st.markdown("""
        <div class="glass-card">
            <h3><span class="material-symbols-outlined" style="font-size:20px">info</span> Dashboard</h3>
            <p>Ejecuta <code>IA_agente_Camanchaca5.ipynb</code> para generar el dashboard de observabilidad.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h2 style='font-family:var(--font-heading);font-size:20px;font-weight:600;color:var(--color-primary-dark)'>🔍 Trazabilidad (IL3.2 / IE10)</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
        <p>• <strong>Trace ID único</strong> por consulta (UUID)<br>
        • <strong>3 etapas</strong>: validación de entrada → identificación de centro → invocación del agente<br>
        • <strong>Analizador de trazas</strong>: identifica etapa más lenta y puntos de falla<br>
        • <strong>Formato JSON estructurado</strong> para auditoría</p>
        <hr style="margin:12px 0">
        <p><strong>Hallazgos:</strong><br>
        • La etapa <code>invocacion_agente</code> concentra &gt;90% de la latencia (~3.8s)<br>
        • Mensajes vacíos generan trazas con error (validación temprana agregada)</p>
    </div>
    """, unsafe_allow_html=True)

elif pagina == "Seguridad":
    encabezado_seccion("Seguridad y Uso Responsable", "IL3.3 / IE11 — GUARDRAILS, ÉTICA Y PRIVACIDAD", "shield")

    st.markdown("""
    <div class="glass-card">
        <h3><span class="material-symbols-outlined" style="font-size:20px">verified</span> Pipeline de Seguridad</h3>
        <p>1. <strong>Rate Limiting</strong> → 10 peticiones/minuto (límite GitHub Models)<br>
        2. <strong>Anti-Prompt Injection</strong> → 8 patrones regex bloqueados<br>
        3. <strong>Filtro Ético</strong> → 3 categorías: seguridad infraestructura, manipulación datos, riesgo laboral<br>
        4. <strong>Sanitización de PII</strong> → Correos, RUT chilenos, teléfonos redactados<br>
        5. <strong>Invocación del Agente</strong> → Solo si pasa todos los filtros</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h2 style='font-family:var(--font-heading);font-size:20px;font-weight:600;color:var(--color-primary-dark)'>Checklist OWASP LLM Top 10 (IL3.5)</h2>", unsafe_allow_html=True)

    items = [
        ("Prompt Injection bloqueado", "badge-ok", "check"),
        ("Rate limiting (429 en exceso)", "badge-ok", "check"),
        ("PII redactada en respuestas y logs", "badge-ok", "check"),
        ("Errores sin exponer trazas internas", "badge-ok", "check"),
        ("Validación de parámetros antes de APIs externas", "badge-ok", "check"),
        ("HTTPS obligatorio (Caddy)", "badge-ok", "check"),
        ("Contenedores no-root", "badge-ok", "check"),
        ("Security Group restrictivo", "badge-ok", "check"),
    ]

    for desc, estilo, icono in items:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--color-white);border:1px solid var(--color-outline-variant);border-radius:var(--radius-md);margin-bottom:8px">
            <span class="material-symbols-outlined" style="color:var(--color-success);font-size:20px">{icono}</span>
            <span style="font-family:var(--font-body);font-size:14px;color:var(--color-on-surface)">{desc}</span>
            <span style="margin-left:auto" class="badge {estilo}">Cumple</span>
        </div>
        """, unsafe_allow_html=True)

elif pagina == "Despliegue":
    encabezado_seccion("Despliegue en AWS", "IL3.5 — CIBERSEGURIDAD Y DESPLIEGUE EN AWS ACADEMY", "cloud")

    st.markdown("""
    <div class="glass-card">
        <h3><span class="material-symbols-outlined" style="font-size:20px">cloud</span> Arquitectura de Despliegue</h3>
        <pre style="font-size:12px;line-height:1.5;color:var(--color-on-surface-variant);margin:0;background:var(--color-surface-container);padding:16px;border-radius:var(--radius-md);overflow-x:auto">
┌────────────────────────────────────────────────────┐
│              EC2 (Amazon Linux 2023, t3.small)       │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────┐ │
│  │  Caddy   │  │  Frontend  │  │    Backend        │ │
│  │ (proxy)  │◄►│(Streamlit) │◄►│ (Agente +         │ │
│  │ :443/80  │  │            │  │  guardrails)      │ │
│  └────┬─────┘  └────────────┘  └────────┬─────────┘ │
│       │                                  │           │
│       │                 ┌─────────────────▼────────┐ │
│       │                 │  GitHub Models / OpenAI  │ │
│       │                 │  Open-Meteo API         │ │
│       │                 └──────────────────────────┘ │
│  Red interna Docker: solo Caddy expuesto             │
└────────────────────────────────────────────────────┘
        </pre>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='font-family:var(--font-heading);font-size:18px;font-weight:600;color:var(--color-primary-dark);margin-top:24px'><span class='material-symbols-outlined' style='font-size:22px;vertical-align:middle'>checklist</span> Pasos de Despliegue</h2>", unsafe_allow_html=True)

    pasos = [
        "Iniciar laboratorio AWS Academy (rol LabRole)",
        "Crear par de claves SSH (isia-key.pem)",
        "Crear Security Group (isia-sg): HTTP/443 abiertos, SSH solo IP estudiante",
        "Lanzar instancia EC2 t3.small con key pair, SG y rol LabRole",
        "SSH a la instancia e instalar Docker + clonar repositorio",
        "Configurar .env con GITHUB_TOKEN y SITE_ADDRESS",
        "docker compose up -d",
        "Verificar HTTPS en https://<IP_PUBLICA>/api/health",
    ]

    for i, paso in enumerate(pasos, 1):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--color-white);border:1px solid var(--color-outline-variant);border-radius:var(--radius-md);margin-bottom:6px">
            <span style="width:24px;height:24px;border-radius:50%;background:var(--color-primary);color:white;display:flex;align-items:center;justify-content:center;font-family:var(--font-body);font-size:12px;font-weight:700;flex-shrink:0">{i}</span>
            <span style="font-family:var(--font-body);font-size:14px;color:var(--color-on-surface)">{paso}</span>
        </div>
        """, unsafe_allow_html=True)
