import os, re, json, time, requests, streamlit as st
from typing import List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent

load_dotenv()

st.set_page_config(page_title="Salmones Camanchaca — AI Operations Suite", page_icon="🐟", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Hanken+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,0&display=swap" rel="stylesheet">
<style>
:root {
  --primary: #003e6f;
  --primary-dark: #002a4a;
  --primary-container: #005596;
  --on-primary: #ffffff;
  --on-primary-container: #a4caff;
  --secondary: #006688;
  --secondary-container: #43c5fd;
  --surface: #fbf9f8;
  --surface-dim: #dbd9d9;
  --surface-bright: #fbf9f8;
  --surface-container: #efeded;
  --surface-container-low: #f5f3f3;
  --surface-container-high: #eae8e7;
  --surface-container-highest: #e4e2e2;
  --on-surface: #1b1c1c;
  --on-surface-variant: #414750;
  --outline: #727781;
  --outline-variant: #c1c7d2;
  --error: #ba1a1a;
  --error-container: #ffdad6;
  --success: #1e7e34;
  --font-heading: 'Hanken Grotesk', sans-serif;
  --font-body: 'Inter', sans-serif;
  --shadow-sm: 0px 2px 4px rgba(0,85,150,0.05);
  --shadow-md: 0px 4px 12px rgba(0,85,150,0.1);
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
}

.stApp, #root > div:first-child { background: var(--surface); }
section[data-testid="stSidebar"] {
  background: var(--secondary-container) !important;
  min-width: 260px !important;
  border-right: none !important;
}
section[data-testid="stSidebar"] .st-emotion-cache-1gv3huu { background: var(--secondary-container); }

.sidebar-logo { padding: 24px 20px 16px; text-align: center; border-bottom: 1px solid rgba(0,79,107,0.15); margin-bottom: 8px; }
.sidebar-logo img { max-width: 180px; margin-bottom: 12px; }
.sidebar-logo h1 { font-family: var(--font-heading); font-size: 22px; font-weight: 700; color: var(--primary); margin: 0; }
.sidebar-logo p { font-family: var(--font-body); font-size: 11px; font-weight: 600; color: var(--primary); opacity: 0.6; letter-spacing: 0.1em; text-transform: uppercase; margin: 2px 0 0; }

.stSidebar .stRadio { padding: 4px 12px; }
.stSidebar .stRadio > div { display: flex; flex-direction: column; gap: 2px; }
.stSidebar .stRadio label {
  display: flex !important; align-items: center !important; gap: 12px !important;
  padding: 12px 14px !important; border-radius: var(--radius-md) !important;
  font-family: var(--font-body) !important; font-size: 14px !important; font-weight: 400 !important;
  color: var(--primary) !important; opacity: 0.7 !important;
  background: transparent !important; border: none !important;
  transition: all 0.2s ease !important; cursor: pointer !important;
}
.stSidebar .stRadio label:hover { opacity: 1 !important; background: rgba(0,85,150,0.08) !important; }
.stSidebar .stRadio label[data-selected="true"] {
  background: var(--primary-container) !important; color: var(--on-primary) !important; opacity: 1 !important; font-weight: 600 !important;
  box-shadow: var(--shadow-sm) !important;
}
.stSidebar .stRadio label[data-selected="true"]::before { color: var(--on-primary) !important; opacity: 1 !important; }

.stSidebar .stRadio label::before {
  font-family: 'Material Symbols Outlined'; font-size: 20px; width: 24px; text-align: center;
  display: inline-block; opacity: 0.6; transition: opacity 0.2s;
}
.stSidebar .stRadio label:hover::before { opacity: 1; }
.stSidebar .stRadio div[role="radiogroup"] > div:nth-child(1) label::before { content: "dashboard"; }
.stSidebar .stRadio div[role="radiogroup"] > div:nth-child(2) label::before { content: "smart_toy"; }
.stSidebar .stRadio div[role="radiogroup"] > div:nth-child(3) label::before { content: "book"; }
.stSidebar .stRadio div[role="radiogroup"] > div:nth-child(4) label::before { content: "account_tree"; }
.stSidebar .stRadio div[role="radiogroup"] > div:nth-child(5) label::before { content: "monitoring"; }
.stSidebar .stRadio div[role="radiogroup"] > div:nth-child(6) label::before { content: "shield"; }
.stSidebar .stRadio div[role="radiogroup"] > div:nth-child(7) label::before { content: "cloud"; }

.sidebar-btn {
  margin: 12px 16px !important; padding: 12px !important; border-radius: var(--radius-lg) !important;
  background: var(--primary-container) !important; color: var(--on-primary) !important;
  font-family: var(--font-body) !important; font-weight: 600 !important; font-size: 14px !important;
  border: none !important; transition: all 0.2s !important; cursor: pointer !important; width: calc(100% - 32px) !important;
}
.sidebar-btn:hover { opacity: 0.9 !important; box-shadow: var(--shadow-md) !important; }
.sidebar-footer { border-top: 1px solid rgba(0,79,107,0.1); padding: 16px 20px; text-align: center; margin-top: 8px; }
.sidebar-footer a {
  display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: var(--radius-md);
  font-family: var(--font-body); font-size: 13px; color: var(--primary); opacity: 0.6;
  text-decoration: none; transition: all 0.2s; cursor: pointer;
}
.sidebar-footer a:hover { opacity: 1; background: rgba(0,85,150,0.06); }
.sidebar-footer a span { font-size: 18px; }

.main-header { font-family: var(--font-heading); font-size: 32px; font-weight: 700; color: var(--primary); margin-bottom: 4px; }
.sub-header { font-family: var(--font-body); font-size: 16px; font-weight: 400; color: var(--on-surface-variant); margin: 0 0 24px; }
.section-title { font-family: var(--font-body); font-size: 12px; font-weight: 600; color: var(--secondary); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }

.glass-card {
  background: var(--surface-bright); border: 1px solid var(--outline-variant); border-radius: var(--radius-lg);
  padding: 20px 24px; box-shadow: var(--shadow-sm); transition: all 0.3s ease; margin-bottom: 16px;
}
.glass-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.glass-card h3 { font-family: var(--font-heading); font-size: 18px; font-weight: 600; color: var(--primary); margin: 0 0 12px; display: flex; align-items: center; gap: 8px; }
.glass-card p { font-family: var(--font-body); font-size: 14px; color: var(--on-surface-variant); line-height: 1.6; margin: 0; }

.badge { display: inline-flex; align-items: center; padding: 3px 10px; border-radius: 20px; font-family: var(--font-body); font-size: 11px; font-weight: 600; letter-spacing: 0.03em; }
.badge-ok { background: #e6f4ea; color: var(--success); }
.badge-info { background: #e8f0fe; color: var(--primary-container); }
.badge-error { background: #fce8e6; color: var(--error); }

.metric-card {
  background: var(--surface-bright); border: 1px solid var(--outline-variant); border-radius: var(--radius-md);
  padding: 16px 20px; box-shadow: var(--shadow-sm); transition: all 0.3s ease; text-align: center;
}
.metric-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.metric-card .metric-value { font-family: var(--font-heading); font-size: 28px; font-weight: 700; color: var(--primary); line-height: 1.2; }
.metric-card .metric-label { font-family: var(--font-body); font-size: 12px; font-weight: 600; color: var(--outline); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }
.metric-card .metric-delta { font-family: var(--font-body); font-size: 12px; color: var(--outline); margin-top: 2px; }

.notebook-card {
  background: var(--surface-bright); border: 1px solid var(--outline-variant); border-radius: var(--radius-md);
  padding: 16px 20px; box-shadow: var(--shadow-sm); transition: all 0.3s ease; margin-bottom: 12px;
}
.notebook-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.notebook-card .nb-title { font-family: var(--font-heading); font-size: 16px; font-weight: 600; color: var(--primary); }
.notebook-card .nb-section { font-family: var(--font-body); font-size: 11px; font-weight: 600; color: var(--secondary); letter-spacing: 0.05em; text-transform: uppercase; }
.notebook-card .nb-desc { font-family: var(--font-body); font-size: 14px; font-weight: 600; color: var(--on-surface); margin: 4px 0; }
.notebook-card .nb-detail { font-family: var(--font-body); font-size: 13px; color: var(--on-surface-variant); line-height: 1.5; }

.stButton > button {
  font-family: var(--font-body) !important; font-weight: 600 !important;
  border-radius: var(--radius-md) !important; padding: 8px 20px !important;
  transition: all 0.2s ease !important; border: none !important;
}
.stButton > button[kind="primary"] { background: var(--primary-container) !important; color: var(--on-primary) !important; }
.stButton > button[kind="primary"]:hover { background: var(--primary) !important; box-shadow: var(--shadow-md) !important; }
.stButton > button[kind="secondary"] { background: transparent !important; color: var(--primary-container) !important; border: 1.5px solid var(--primary-container) !important; }
.stButton > button[kind="secondary"]:hover { background: rgba(0,85,150,0.05) !important; }

h1,h2,h3,h4,h5,h6 { font-family: var(--font-heading) !important; color: var(--primary) !important; }
p,li,.stMarkdown { font-family: var(--font-body) !important; color: var(--on-surface) !important; }
code { font-family: 'JetBrains Mono','Fira Code',monospace !important; font-size: 13px !important; }
hr { border-color: var(--outline-variant) !important; margin: 24px 0 !important; opacity: 0.5; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--outline-variant); border-radius: 10px; }

.stInfo { background: #e8f0fe !important; border: 1px solid #c5d9f2 !important; border-radius: var(--radius-md) !important; font-family: var(--font-body) !important; font-size: 13px !important; color: var(--on-surface-variant) !important; }
.st-emotion-cache-1gwvy38, .element-container:has(>div>div>.stSidebarNavItems) { display: none; }

.quick-actions { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.quick-action-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; background: var(--surface-bright); border: 1px solid var(--outline-variant);
  border-radius: 9999px; font-family: var(--font-body); font-size: 13px; font-weight: 500;
  color: var(--on-surface-variant); cursor: pointer;
  transition: all 0.2s ease; white-space: nowrap;
}
.quick-action-btn:hover { border-color: var(--primary-container); color: var(--primary-container); }
.quick-action-btn span { font-size: 16px; }

.chat-container { max-width: 900px; margin: 0 auto; padding: 0 4px; }
.chat-msg { display: flex; margin-bottom: 20px; animation: fadeIn 0.3s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.chat-msg.user { justify-content: flex-end; }
.chat-msg.ai { justify-content: flex-start; gap: 12px; }
.chat-msg .avatar {
  width: 40px; height: 40px; border-radius: 50%; background: var(--primary-container);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: var(--shadow-sm);
}
.chat-msg .avatar span { color: var(--on-primary); font-size: 20px; }
.chat-msg .bubble {
  padding: 14px 18px; max-width: 72%; font-family: var(--font-body); font-size: 14px; line-height: 1.6;
  color: var(--on-surface); box-shadow: var(--shadow-sm);
}
.chat-msg.user .bubble {
  background: var(--surface-container-high); border-radius: 18px 18px 4px 18px;
}
.chat-msg.ai .bubble {
  background: var(--surface-bright); border-radius: 18px 18px 18px 4px; border: 1px solid var(--outline-variant);
}
.chat-msg .timestamp {
  display: block; font-family: var(--font-body); font-size: 11px; color: var(--on-surface-variant); opacity: 0.6; margin-top: 6px;
}
.chat-msg .feedback { display: flex; gap: 4px; margin-top: 8px; padding-left: 4px; }
.chat-msg .feedback button {
  width: 32px; height: 32px; border-radius: 50%; border: none; background: transparent;
  color: var(--on-surface-variant); cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; opacity: 0.5;
}
.chat-msg .feedback button:hover { background: var(--surface-container-high); opacity: 1; }
.chat-msg .feedback button span { font-size: 18px; }

.data-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-top: 14px; }
.data-card {
  background: var(--surface-container-lowest, #fff); border: 1px solid var(--outline-variant);
  border-radius: var(--radius-lg); padding: 14px 16px; box-shadow: var(--shadow-sm); transition: all 0.2s ease;
}
.data-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
.data-card .dc-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.data-card .dc-header span:first-child { font-size: 20px; color: var(--secondary); }
.data-card .dc-label { font-family: var(--font-body); font-size: 11px; font-weight: 600; color: var(--on-surface-variant); text-transform: uppercase; letter-spacing: 0.04em; }
.data-card .dc-value { font-family: var(--font-heading); font-size: 22px; font-weight: 700; color: var(--primary); line-height: 1.3; }
.data-card .dc-bar { height: 4px; background: var(--secondary-container); border-radius: 999px; margin-top: 8px; overflow: hidden; }
.data-card .dc-bar-fill { height: 100%; background: var(--secondary); border-radius: 999px; }
.data-card.optimal { border-color: rgba(30,126,52,0.3); background: rgba(230,244,234,0.4); }
.data-card.optimal .dc-value { color: var(--success); }
.data-card.optimal .dc-label { color: var(--success); }

.stChatFloatingInputContainer, div[data-testid="stChatInput"] {
  border: 1.5px solid var(--outline-variant) !important; border-radius: var(--radius-2xl) !important;
  background: var(--surface-bright) !important; box-shadow: var(--shadow-sm) !important;
  padding: 6px 6px 6px 16px !important; max-width: 800px !important; margin: 0 auto !important;
}
div[data-testid="stChatInput"]:focus-within { border-color: var(--primary-container) !important; box-shadow: 0 0 0 3px rgba(0,85,150,0.1) !important; }
div[data-testid="stChatInput"] input { font-family: var(--font-body) !important; font-size: 14px !important; }
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

pagina = st.sidebar.radio("Navegación", ["Inicio","Chatbot","Notebooks","Arquitectura","Observabilidad","Seguridad","Despliegue"], label_visibility="collapsed")

if pagina == "Chatbot":
    st.sidebar.markdown(f'<button class="sidebar-btn" onclick="alert(\'Nuevo análisis\')"><span class="material-symbols-outlined" style="font-size:18px;vertical-align:middle;margin-right:6px">add</span> New Analysis</button>', unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-footer">
    <a><span class="material-symbols-outlined">help_center</span> Support</a>
    <a><span class="material-symbols-outlined">settings</span> Settings</a>
</div>
""", unsafe_allow_html=True)

def encabezado(titulo, subtitulo=None):
    st.markdown(f"<p class='section-title'>{subtitulo or ''}</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='main-header'>{titulo}</h1>", unsafe_allow_html=True)

# ─── CHATBOT ─────────────────────────────────────────────────────────────────
if pagina == "Chatbot":
    CENTROS = {
        "ensenada": {"lat": -41.140459, "lon": -72.404236, "nombre": "Piscicultura Petrohué"},
        "puelche":  {"lat": -41.733,    "lon": -73.602,    "nombre": "Centro Puelche"},
        "huito":    {"lat": -41.783,    "lon": -73.583,    "nombre": "Centro Huito (San José)"},
    }

    def _get_clima_actual(centro: str) -> str:
        if centro.lower() not in CENTROS:
            return f"Centro '{centro}' no encontrado. Opciones: ensenada, puelche, huito."
        datos = CENTROS[centro.lower()]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={datos['lat']}&longitude={datos['lon']}&current=temperature_2m,wind_speed_10m,precipitation,weathercode&timezone=America/Santiago"
        try:
            r = requests.get(url, timeout=10).json()["current"]
            cond = "Despejado" if r["weathercode"] < 3 else "Nublado" if r["weathercode"] < 50 else "Lluvia"
            return f"{{\"centro\":\"{datos['nombre']}\",\"temp\":{r['temperature_2m']},\"viento\":{r['wind_speed_10m']},\"lluvia\":{r['precipitation']},\"condicion\":\"{cond}\"}}"
        except Exception as e:
            return f'{{"error":"{e}"}}'

    def _get_pronostico_semana(centro: str) -> str:
        if centro.lower() not in CENTROS:
            return f"Centro '{centro}' no encontrado."
        datos = CENTROS[centro.lower()]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={datos['lat']}&longitude={datos['lon']}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weathercode&timezone=America/Santiago"
        try:
            d = requests.get(url, timeout=10).json()["daily"]
            items = []
            for i in range(7):
                c = "Despejado" if d["weathercode"][i] < 3 else "Nublado" if d["weathercode"][i] < 50 else "Lluvia"
                items.append({"fecha":d["time"][i],"tmax":d["temperature_2m_max"][i],"tmin":d["temperature_2m_min"][i],"lluvia":d["precipitation_sum"][i],"viento":d["wind_speed_10m_max"][i],"condicion":c})
            return json.dumps({"centro":datos['nombre'],"dias":items})
        except Exception as e:
            return f'{{"error":"{e}"}}'

    tools_agente = [
        StructuredTool.from_function(func=_get_clima_actual, name="get_clima_actual", description="Obtiene el clima actual para un centro. Parametro: ensenada, puelche, huito."),
        StructuredTool.from_function(func=_get_pronostico_semana, name="get_pronostico_semana", description="Obtiene el pronostico de 7 dias para un centro. Parametro: ensenada, puelche, huito."),
    ]
    agent_executor = create_react_agent(
        ChatOpenAI(base_url=os.getenv("OPENAI_BASE_URL"), api_key=os.getenv("GITHUB_TOKEN"), model="gpt-4o", temperature=0, request_timeout=600),
        tools_agente,
    )

    INJECTION = [r"ignora(?:r)?\s+(?:las\s+)?instrucciones", r"olvida(?:r)?\s+tus\s+instrucciones", r"eres\s+ahora\s+un", r"revela\s+tu\s+system\s*prompt", r"actua\s+como\s+si\s+no\s+tuvieras\s+reglas", r"sin\s+restricciones", r"bypassea(?:r)?\s+las?\s+seguridad", r"ignora\s+todas?\s+las?\s+reglas"]
    PII = {"correo": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "telefono": re.compile(r"(?:\+56\s?)?(?:9\s?\d{4}\s?\d{4}|\d{2}\s?\d{3}\s?\d{4})"), "rut": re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK]\b")}

    def validar(t): return (False, "Intento de prompt injection detectado.") if any(re.search(p, t.lower()) for p in INJECTION) else (True, "")
    def sanitizar(t):
        for p in PII.values(): t = p.sub("[PII_REDACTADO]", t)
        return t

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
        st.session_state.historial = []

    def render_data_cards(data_text):
        try:
            d = json.loads(data_text)
            if "temp" in d:
                temp_pct = min(100, max(0, int((d["temp"] / 30) * 100)))
                wind_pct = min(100, max(0, int((d["viento"] / 50) * 100)))
                return f"""
                <div class="data-cards">
                    <div class="data-card">
                        <div class="dc-header"><span class="material-symbols-outlined">device_thermostat</span><span class="dc-label">Temperatura</span></div>
                        <div class="dc-value">{d['temp']}°C</div>
                        <div class="dc-bar"><div class="dc-bar-fill" style="width:{temp_pct}%"></div></div>
                    </div>
                    <div class="data-card">
                        <div class="dc-header"><span class="material-symbols-outlined">air</span><span class="dc-label">Viento</span></div>
                        <div class="dc-value">{d['viento']} km/h</div>
                        <div class="dc-bar"><div class="dc-bar-fill" style="width:{wind_pct}%"></div></div>
                    </div>
                    <div class="data-card optimal">
                        <div class="dc-header"><span class="material-symbols-outlined">check_circle</span><span class="dc-label">Estado</span></div>
                        <div class="dc-value">{d['condicion']}</div>
                        <p style="font-size:11px;color:var(--success);margin:4px 0 0;font-weight:500">Safe to proceed</p>
                    </div>
                </div>
                """
        except: pass
        try:
            d = json.loads(data_text)
            if "dias" in d:
                items = "".join(f'<div class="data-card" style="text-align:center;padding:10px"><div class="dc-label">{di["fecha"][-5:]}</div><div class="dc-value" style="font-size:16px">{di["tmin"]}°-{di["tmax"]}°</div><div style="font-size:11px;color:var(--on-surface-variant)">{di["condicion"]}</div></div>' for di in d["dias"])
                return f'<div class="data-cards" style="grid-template-columns:repeat(7,1fr)">{items}</div>'
        except: pass
        return ""

    def render_msg(msg):
        role = msg["role"]
        content = msg["content"]
        ts = time.strftime("%I:%M %p")
        if role == "user":
            return f'<div class="chat-msg user"><div class="bubble">{content}<span class="timestamp">{ts}</span></div></div>'
        cards = render_data_cards(content) if "temp" in content or "dias" in content else ""
        return f'''
        <div class="chat-msg ai">
            <div class="avatar"><span class="material-symbols-outlined">smart_toy</span></div>
            <div>
                <div class="bubble">{content}{cards}</div>
                <div class="feedback">
                    <button><span class="material-symbols-outlined">thumb_up</span></button>
                    <button><span class="material-symbols-outlined">thumb_down</span></button>
                    <button><span class="material-symbols-outlined">content_copy</span></button>
                </div>
            </div>
        </div>'''

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    st.markdown('<div class="quick-actions">', unsafe_allow_html=True)
    for label, icon in [("Pronóstico 7 días","calendar_month"), ("Estado de Jaulas","grid_view"), ("Análisis de Oxígeno","bubble_chart")]:
        st.markdown(f'<button class="quick-action-btn" onclick="navigator.clipboard.writeText(\'{label}\')"><span class="material-symbols-outlined">{icon}</span>{label}</button>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    for msg in st.session_state.mensajes:
        st.markdown(render_msg(msg), unsafe_allow_html=True)

    if prompt := st.chat_input("Describe una consulta o solicita un reporte..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        st.markdown(render_msg({"role": "user", "content": prompt}), unsafe_allow_html=True)

        valida, motivo = validar(prompt)
        if not valida:
            respuesta = f"🚫 {motivo}"
            st.markdown(render_msg({"role": "assistant", "content": respuesta}), unsafe_allow_html=True)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        else:
            st.session_state.historial.append(("human", sanitizar(prompt)))
            with st.spinner("Analizando datos en tiempo real..."):
                try:
                    response = agent_executor.invoke({"messages": st.session_state.historial[-6:]})
                    respuesta = sanitizar(response["messages"][-1].content)
                except Exception as e:
                    respuesta = "Error al procesar la consulta."
            st.markdown(render_msg({"role": "assistant", "content": respuesta}), unsafe_allow_html=True)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
            st.session_state.historial.append(("ai", respuesta))

    st.markdown('</div>', unsafe_allow_html=True)

# ─── INICIO ──────────────────────────────────────────────────────────────────
elif pagina == "Inicio":
    encabezado("Sistema de Agentes Camanchaca", "MONITOREO CLIMÁTICO Y OPERACIONAL")
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">description</span> Resumen del Proyecto</h3><p>Sistema multi-agente para <strong>Salmones Camanchaca</strong> que automatiza el monitoreo de condiciones climáticas en centros de cultivo de la Región de Los Lagos (<strong>Ensenada, Puelche y Huito</strong>). Los agentes consultan APIs externas, mantienen memoria conversacional y aplican RAG para fundamentar decisiones operativas.</p></div>', unsafe_allow_html=True)
        ca, cb, cc = st.columns(3)
        with ca: st.markdown('<div class="metric-card"><div class="metric-value">12</div><div class="metric-label">Notebooks</div><div class="metric-delta">IA, CoT, RAG, Agentes</div></div>', unsafe_allow_html=True)
        with cb: st.markdown('<div class="metric-card"><div class="metric-value">4</div><div class="metric-label">Herramientas</div><div class="metric-delta">Clima, Pronóstico, Evaluación</div></div>', unsafe_allow_html=True)
        with cc: st.markdown('<div class="metric-card"><div class="metric-value">3</div><div class="metric-label">Centros</div><div class="metric-delta">Ensenada, Puelche, Huito</div></div>', unsafe_allow_html=True)
    with col2:
        if os.path.exists("dashboard_observabilidad_camanchaca.png"):
            st.image("dashboard_observabilidad_camanchaca.png", caption="Dashboard de Observabilidad", use_container_width=True)
        else:
            st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">info</span> Dashboard</h3><p>Ejecuta <code>IA_agente_Camanchaca5.ipynb</code> para generarlo.</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='font-size:22px'>🧱 Stack Tecnológico</h2>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (n, ic) in enumerate([("Python 3.11","🐍"),("LangChain","⛓️"),("LangGraph","🕸️"),("CrewAI","🤖"),("OpenAI/GitHub Models","🧠")]):
        cols[i].markdown(f'<div class="glass-card" style="text-align:center;padding:16px"><div style="font-size:32px;margin-bottom:8px">{ic}</div><div style="font-family:var(--font-body);font-size:13px;font-weight:600;color:var(--primary)">{n}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='font-size:22px'>📂 Estructura del Proyecto</h2>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><pre style="font-size:13px;line-height:1.6;color:var(--on-surface-variant);margin:0;background:var(--surface-container);padding:16px;border-radius:var(--radius-md);overflow-x:auto">IA_Camanchaca_ChatBot/\n├── IA_Camanchaca.ipynb          # Chatbot base con memoria\n├── IA_Camanchaca2.ipynb         # Chain-of-Thought + Few-Shot\n├── IA_Camanchaca3.ipynb         # RAG con FAISS vector store\n├── IA_agente_Camanchaca1.ipynb  # Agente ReAct + Function Calling + CrewAI\n├── IA_agente_Camanchaca2.ipynb  # Memoria: Buffer, Window y Summary\n├── IA_agente_Camanchaca3.ipynb  # Planificación y orquestación\n├── IA_agente_Camanchaca4.ipynb  # Arquitectura y buenas prácticas\n├── IA_agente_Camanchaca5.ipynb  # Observabilidad y métricas (IL3.1)\n├── IA_agente_Camanchaca6.ipynb  # Trazabilidad y logs (IL3.2)\n├── IA_agente_Camanchaca7.ipynb  # Seguridad y ética (IL3.3)\n├── IA_agente_Camanchaca8.ipynb  # Escalabilidad y sostenibilidad (IL3.4)\n├── IA_agente_Camanchaca9.ipynb  # Ciberseguridad y despliegue AWS (IL3.5)\n├── bot.py\n├── app.py                       # Esta aplicación Streamlit\n├── requirements.txt\n└── .env</pre></div>', unsafe_allow_html=True)

# ─── NOTEBOOKS ───────────────────────────────────────────────────────────────
elif pagina == "Notebooks":
    encabezado("Explorador de Notebooks", "12 NOTEBOOKS — LÍNEAS DE APRENDIZAJE IL1 A IL3")
    for s, n, d, e, det in [
        ("IL1.1-IL1.4","IA_Camanchaca.ipynb","Chatbot base con LangChain","✅","Chatbot conversacional con streaming, memoria de sesión y system prompt para acuicultura."),
        ("IL2.1","IA_Camanchaca2.ipynb","Chain-of-Thought + Few-Shot","✅","Razonamiento estructurado paso a paso con ejemplos few-shot para mortalidad, FCR y biometrías."),
        ("IL2.2","IA_Camanchaca3.ipynb","RAG con FAISS","✅","Retrieval-Augmented Generation usando FAISS como vector store."),
        ("IL2.3","IA_agente_Camanchaca1.ipynb","Agente ReAct + Function Calling + CrewAI","✅","Ciclo ReAct, Function Calling y multi-agente con CrewAI."),
        ("IL2.4","IA_agente_Camanchaca2.ipynb","Memoria (Buffer, Window, Summary)","✅","Tres estrategias de memoria conversacional comparadas."),
        ("IL2.5","IA_agente_Camanchaca3.ipynb","Planificación y Orquestación","✅","Planificación jerárquica, reactiva y por objetivos."),
        ("IL2.6","IA_agente_Camanchaca4.ipynb","Arquitectura y Buenas Prácticas","✅","Arquitectura en capas, configuración centralizada, DRY, pruebas unitarias."),
        ("IL3.1","IA_agente_Camanchaca5.ipynb","Observabilidad y Métricas (IE9)","✅","Logging estructurado, métricas de latencia, precisión y consistencia."),
        ("IL3.2","IA_agente_Camanchaca6.ipynb","Trazabilidad y Logs (IE10)","✅","Trace IDs únicos, trazas JSON, analizador de puntos de falla."),
        ("IL3.3","IA_agente_Camanchaca7.ipynb","Seguridad y Ética (IE11)","✅","Anti-prompt injection, PII, filtro ético, rate limiting."),
        ("IL3.4","IA_agente_Camanchaca8.ipynb","Escalabilidad y Sostenibilidad (IE12)","✅","CacheLLM, enrutamiento de modelos, procesamiento por lotes."),
        ("IL3.5","IA_agente_Camanchaca9.ipynb","Ciberseguridad y Despliegue AWS","✅","Guardrails, OWASP LLM Top 10, EC2 + Caddy + Docker."),
    ]:
        st.markdown(f'<div class="notebook-card"><div style="display:flex;justify-content:space-between;align-items:start"><div><span class="nb-section">{s}</span><div class="nb-title">{n}</div></div><span class="badge badge-ok">{e}</span></div><div class="nb-desc">{d}</div><div class="nb-detail">{det}</div></div>', unsafe_allow_html=True)

# ─── ARQUITECTURA ────────────────────────────────────────────────────────────
elif pagina == "Arquitectura":
    encabezado("Arquitectura del Sistema", "CAPAS, COMPONENTES Y FLUJO DE DATOS")
    st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">account_tree</span> Diagrama de Arquitectura</h3><pre style="font-size:12px;line-height:1.5;color:var(--on-surface-variant);margin:0;background:var(--surface-container);padding:16px;border-radius:var(--radius-md);overflow-x:auto">\n┌─────────────────────────────────────────────────────────────────┐\n│                    OPERADOR CAMANCHACA                           │\n│              (Consulta en lenguaje natural)                      │\n└────────────────────────┬────────────────────────────────────────┘\n                         │\n                         ▼\n┌─────────────────────────────────────────────────────────────────┐\n│              CAPA DE PRESENTACIÓN (Streamlit / Jupyter)          │\n└────────────────────────┬────────────────────────────────────────┘\n                         │\n                         ▼\n┌─────────────────────────────────────────────────────────────────┐\n│              CAPA DE APLICACIÓN — AGENTES                        │\n│  ┌──────────────┐  ┌────────────────┐  ┌────────────────────┐   │\n│  │  Agente ReAct │  │  Memoria de    │  │  Crew Multi-Agente │   │\n│  │  (LangGraph)  │  │  Sesión        │  │  (CrewAI)          │   │\n│  └──────┬───────┘  └───────┬────────┘  └─────────┬──────────┘   │\n│         └──────────────────┴──────────────────────┘              │\n│                              ▼                                   │\n│              ┌────────────────────────────┐                      │\n│              │  Gestor de Herramientas     │                      │\n│              └────────────────────────────┘                      │\n└────────────────────────┬────────────────────────────────────────┘\n                         │\n                         ▼\n┌─────────────────────────────────────────────────────────────────┐\n│              CAPA DE DOMINIO — HERRAMIENTAS                      │\n│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │\n│  │ get_clima_   │  │get_pronostico│  │ evaluar_operacion    │   │\n│  │ actual       │  │_semana       │  │                      │   │\n│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │\n│         ▼                 ▼                      ▼               │\n│  ┌──────────────────────────────────────────────────────────┐   │\n│  │              API Open-Meteo (gratuita, sin key)           │   │\n│  └──────────────────────────────────────────────────────────┘   │\n│  ┌──────────────────────────────────────────────────────────┐   │\n│  │              FAISS Vector Store (RAG)                     │   │\n│  └──────────────────────────────────────────────────────────┘   │\n└────────────────────────┬────────────────────────────────────────┘\n                         │\n                         ▼\n┌─────────────────────────────────────────────────────────────────┐\n│              CAPA DE INFRAESTRUCTURA                             │\n│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │\n│  │   GitHub     │  │   LangSmith  │  │  AWS EC2 (Caddy +    │   │\n│  │ Models API   │  │   Tracing    │  │  Docker)             │   │\n│  └──────────────┘  └──────────────┘  └──────────────────────┘   │\n└─────────────────────────────────────────────────────────────────┘\n</pre></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:20px;margin-top:24px'>🧠 Componentes Clave</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">sync_alt</span> LangGraph (ReAct)</h3><p>• Ciclo <strong>Razonar → Actuar → Observar</strong><br>• Nativo en LangChain 1.3+<br>• Manejo de herramientas con @tool decorator</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">groups</span> CrewAI (Multi-Agente)</h3><p>• <strong>Meteorólogo Acuícola</strong>: clima y pronóstico<br>• <strong>Coordinador Operaciones</strong>: planificación<br>• <strong>Supervisor General</strong>: reporte ejecutivo</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">memory</span> Memoria Conversacional</h3><p>• <code>InMemoryChatMessageHistory</code>: sesiones<br>• <code>ConversationBufferMemory</code>: historial completo<br>• <code>ConversationWindowMemory</code>: ventana k=2<br>• <code>ConversationSummaryMemory</code>: resumen automático</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">database</span> RAG con FAISS</h3><p>• Embeddings: <code>text-embedding-3-small</code><br>• Chunk size: 400, overlap: 60<br>• Retrieve: top-k=2 por consulta</p></div>', unsafe_allow_html=True)

# ─── OBSERVABILIDAD ──────────────────────────────────────────────────────────
elif pagina == "Observabilidad":
    encabezado("Observabilidad y Métricas", "IL3.1 / IE9 — PRECISIÓN, LATENCIA Y CONSISTENCIA")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-value">4,253 ms</div><div class="metric-label">Latencia Promedio</div><div class="metric-delta">±10.75% CV</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><div class="metric-value">80%</div><div class="metric-label">Precisión</div><div class="metric-delta">Resp. con datos numéricos</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><div class="metric-value">100%</div><div class="metric-label">Tasa de Éxito</div><div class="metric-delta">Sin errores en 5 consultas</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-card"><div class="metric-value">302</div><div class="metric-label">Tokens Totales</div><div class="metric-delta">5 consultas de prueba</div></div>', unsafe_allow_html=True)
    if os.path.exists("dashboard_observabilidad_camanchaca.png"):
        st.image("dashboard_observabilidad_camanchaca.png", caption="Dashboard de Observabilidad — Latencia y Precisión por Consulta", use_container_width=True)
    else:
        st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">info</span> Dashboard</h3><p>Ejecuta <code>IA_agente_Camanchaca5.ipynb</code> para generar el dashboard.</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='font-size:20px'>🔍 Trazabilidad (IL3.2 / IE10)</h2>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card"><p>• <strong>Trace ID único</strong> por consulta (UUID)<br>• <strong>3 etapas</strong>: validación → identificación → invocación del agente<br>• <strong>Analizador de trazas</strong>: identifica etapa más lenta y puntos de falla<br>• <strong>Formato JSON estructurado</strong> para auditoría</p><hr style="margin:12px 0"><p><strong>Hallazgos:</strong><br>• La etapa <code>invocacion_agente</code> concentra &gt;90% de la latencia (~3.8s)<br>• Mensajes vacíos generan trazas con error (validación temprana agregada)</p></div>', unsafe_allow_html=True)

# ─── SEGURIDAD ───────────────────────────────────────────────────────────────
elif pagina == "Seguridad":
    encabezado("Seguridad y Uso Responsable", "IL3.3 / IE11 — GUARDRAILS, ÉTICA Y PRIVACIDAD")
    st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">verified</span> Pipeline de Seguridad</h3><p>1. <strong>Rate Limiting</strong> → 10 peticiones/minuto<br>2. <strong>Anti-Prompt Injection</strong> → 8 patrones regex bloqueados<br>3. <strong>Filtro Ético</strong> → 3 categorías: seguridad infraestructura, manipulación datos, riesgo laboral<br>4. <strong>Sanitización de PII</strong> → Correos, RUT chilenos, teléfonos redactados<br>5. <strong>Invocación del Agente</strong> → Solo si pasa todos los filtros</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h2 style='font-size:20px'>Checklist OWASP LLM Top 10 (IL3.5)</h2>", unsafe_allow_html=True)
    for desc in ["Prompt Injection bloqueado","Rate limiting (429 en exceso)","PII redactada en respuestas y logs","Errores sin exponer trazas internas","Validación de parámetros antes de APIs externas","HTTPS obligatorio (Caddy)","Contenedores no-root","Security Group restrictivo"]:
        st.markdown(f'<div style="display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--surface-bright);border:1px solid var(--outline-variant);border-radius:var(--radius-md);margin-bottom:8px"><span class="material-symbols-outlined" style="color:var(--success);font-size:20px">check</span><span style="font-family:var(--font-body);font-size:14px">{desc}</span><span style="margin-left:auto" class="badge badge-ok">Cumple</span></div>', unsafe_allow_html=True)

# ─── DESPLIEGUE ──────────────────────────────────────────────────────────────
elif pagina == "Despliegue":
    encabezado("Despliegue en AWS", "IL3.5 — CIBERSEGURIDAD Y DESPLIEGUE EN AWS ACADEMY")
    st.markdown('<div class="glass-card"><h3><span class="material-symbols-outlined" style="font-size:20px">cloud</span> Arquitectura de Despliegue</h3><pre style="font-size:12px;line-height:1.5;color:var(--on-surface-variant);margin:0;background:var(--surface-container);padding:16px;border-radius:var(--radius-md);overflow-x:auto">\n┌────────────────────────────────────────────────────┐\n│              EC2 (Amazon Linux 2023, t3.small)       │\n│  ┌──────────┐  ┌────────────┐  ┌──────────────────┐ │\n│  │  Caddy   │  │  Frontend  │  │    Backend        │ │\n│  │ (proxy)  │◄►│(Streamlit) │◄►│ (Agente +         │ │\n│  │ :443/80  │  │            │  │  guardrails)      │ │\n│  └────┬─────┘  └────────────┘  └────────┬─────────┘ │\n│       │                                  │           │\n│       │                 ┌─────────────────▼────────┐ │\n│       │                 │  GitHub Models / OpenAI  │ │\n│       │                 │  Open-Meteo API         │ │\n│       │                 └──────────────────────────┘ │\n│  Red interna Docker: solo Caddy expuesto             │\n└────────────────────────────────────────────────────┘\n</pre></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:18px;margin-top:24px'>Pasos de Despliegue</h2>", unsafe_allow_html=True)
    for i, paso in enumerate(["Iniciar laboratorio AWS Academy (rol LabRole)","Crear par de claves SSH (isia-key.pem)","Crear Security Group (isia-sg): HTTP/443 abiertos, SSH solo IP estudiante","Lanzar instancia EC2 t3.small con key pair, SG y rol LabRole","SSH a la instancia e instalar Docker + clonar repositorio","Configurar .env con GITHUB_TOKEN y SITE_ADDRESS","docker compose up -d","Verificar HTTPS en https://<IP_PUBLICA>/api/health"], 1):
        st.markdown(f'<div style="display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--surface-bright);border:1px solid var(--outline-variant);border-radius:var(--radius-md);margin-bottom:6px"><span style="width:24px;height:24px;border-radius:50%;background:var(--primary-container);color:white;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0">{i}</span><span style="font-size:14px">{paso}</span></div>', unsafe_allow_html=True)
