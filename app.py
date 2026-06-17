import os
import streamlit as st

st.set_page_config(
    page_title="IA Camanchaca - Sistema de Agentes",
    page_icon="🐟",
    layout="wide",
)

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #1a5276; font-weight: 700; margin-bottom: 0; }
    .sub-header { font-size: 1.1rem; color: #5d6d7e; margin-top: 0; }
    .card { padding: 1.5rem; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 1rem; }
    .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .notebook-title { font-size: 1.1rem; font-weight: 600; color: #1a5276; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-right: 4px; }
    .badge-ok { background: #d5f5e3; color: #1e8449; }
    .badge-warn { background: #fdebd0; color: #b9770e; }
    .badge-info { background: #d6eaf8; color: #1a5276; }
    hr { margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🐟 Camanchaca IA")
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Notebooks", "Arquitectura", "Observabilidad", "Seguridad", "Despliegue"],
)

if pagina == "Inicio":
    st.markdown('<p class="main-header">🐟 Sistema de Agentes Camanchaca</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Monitoreo Climático y Operacional — Salmones Camanchaca · Los Lagos, Chile</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📌 Resumen del Proyecto")
        st.markdown("""
        Sistema multi-agente para **Salmones Camanchaca** que automatiza el monitoreo de
        condiciones climáticas en centros de cultivo de la Región de Los Lagos
        (**Ensenada, Puelche y Huito**). Los agentes consultan APIs externas,
        mantienen memoria conversacional y aplican RAG para fundamentar decisiones operativas.
        """)

        st.markdown("### 🎯 Capacidades")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Notebooks", "12", "IA, CoT, RAG, Agentes")
        with col_b:
            st.metric("Herramientas", "4", "Clima, Pronóstico, Evaluación, Mejor Día")
        with col_c:
            st.metric("Centros", "3", "Ensenada, Puelche, Huito")

    with col2:
        if os.path.exists("dashboard_observabilidad_camanchaca.png"):
            st.image("dashboard_observabilidad_camanchaca.png", caption="Dashboard de Observabilidad", use_container_width=True)
        else:
            st.info("Dashboard no disponible - ejecuta IA_agente_Camanchaca5.ipynb para generarlo")

    st.markdown("---")
    st.markdown("### 🧱 Stack Tecnológico")
    cols = st.columns(5)
    stacks = [("Python 3.11", "🐍"), ("LangChain", "⛓️"), ("LangGraph", "🕸️"), ("CrewAI", "🤖"), ("OpenAI/GitHub Models", "🧠")]
    for i, (name, icon) in enumerate(stacks):
        cols[i].markdown(f"**{icon} {name}**")

    st.markdown("---")
    st.markdown("### 📂 Estructura del Proyecto")
    st.code("""
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
    """)

elif pagina == "Notebooks":
    st.markdown('<p class="main-header">📓 Explorador de Notebooks</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Los 12 notebooks del proyecto, organizados por línea de aprendizaje</p>', unsafe_allow_html=True)
    st.markdown("---")

    notebooks = [
        ("IL1.1-IL1.4", "IA_Camanchaca.ipynb", "Chatbot base con LangChain", "✅", "Chatbot conversacional con streaming, memoria de sesión y sistema prompt para acuicultura. Temperatura baja (0.1) para respuestas técnicas y deterministas."),
        ("IL2.1", "IA_Camanchaca2.ipynb", "Chain-of-Thought + Few-Shot", "✅", "Implementa razonamiento estructurado paso a paso (CoT) con ejemplos few-shot para análisis de mortalidad, FCR y biometrías."),
        ("IL2.2", "IA_Camanchaca3.ipynb", "RAG con FAISS", "✅", "Sistema de Retrieval-Augmented Generation usando FAISS como vector store. Consultas semánticas sobre conocimiento técnico de Camanchaca."),
        ("IL2.3", "IA_agente_Camanchaca1.ipynb", "Agente ReAct + Function Calling + CrewAI", "✅", "Agente con ciclo ReAct, Function Calling de OpenAI, LangGraph y multi-agente con CrewAI (Meteorólogo + Supervisor)."),
        ("IL2.4", "IA_agente_Camanchaca2.ipynb", "Memoria (Buffer, Window, Summary)", "✅", "Tres estrategias de memoria conversacional: Buffer (completa), Window (k=2) y Summary (resumen automático). Comparación de rendimiento."),
        ("IL2.5", "IA_agente_Camanchaca3.ipynb", "Planificación y Orquestación", "✅", "Planificación jerárquica, reactiva y por objetivos. Crew multi-agente con 3 agentes (Meteorólogo, Coordinador, Supervisor)."),
        ("IL2.6", "IA_agente_Camanchaca4.ipynb", "Arquitectura y Buenas Prácticas", "✅", "Documentación formal de arquitectura en capas, configuración centralizada, funciones DRY, validación y pruebas unitarias del sistema."),
        ("IL3.1", "IA_agente_Camanchaca5.ipynb", "Observabilidad y Métricas (IE9)", "✅", "Logging estructurado, métricas de latencia, precisión y consistencia. Dashboard con matplotlib. Wrapper de agente observable."),
        ("IL3.2", "IA_agente_Camanchaca6.ipynb", "Trazabilidad y Logs (IE10)", "✅", "Trace IDs únicos, trazas JSON por etapa, analizador de trazas que identifica puntos de falla y etapas lentas."),
        ("IL3.3", "IA_agente_Camanchaca7.ipynb", "Seguridad y Ética (IE11)", "✅", "Validación anti-prompt injection, detección/sanitización de PII, filtro ético por categorías, rate limiting y pipeline de seguridad integrado."),
        ("IL3.4", "IA_agente_Camanchaca8.ipynb", "Escalabilidad y Sostenibilidad (IE12)", "✅", "CacheLLM, enrutamiento de modelos por complejidad, procesamiento por lotes y propuestas de mejora basadas en datos observados."),
        ("IL3.5", "IA_agente_Camanchaca9.ipynb", "Ciberseguridad y Despliegue AWS", "✅", "Guardrails empaquetados, checklist OWASP LLM Top 10, arquitectura de despliegue EC2 con Caddy HTTPS y Security Group restrictivo."),
    ]

    for i, (seccion, nombre, desc, estado, detalle) in enumerate(notebooks, 1):
        with st.container():
            st.markdown(f"""
            <div class="card">
                <div class="notebook-title">{i:02d}. {nombre}</div>
                <p style="margin:4px 0"><span class="badge badge-info">{seccion}</span> <span class="badge badge-ok">{estado}</span></p>
                <p><strong>{desc}</strong></p>
                <p style="color:#555;font-size:0.9rem">{detalle}</p>
            </div>
            """, unsafe_allow_html=True)

elif pagina == "Arquitectura":
    st.markdown('<p class="main-header">🏗️ Arquitectura del Sistema</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Diagrama de Arquitectura")
    st.markdown("""
```
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
│                                                                   │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────────┐   │
│  │  Agente ReAct │  │  Memoria de    │  │  Crew Multi-Agente │   │
│  │  (LangGraph)  │  │  Sesión        │  │  (CrewAI)          │   │
│  └──────┬───────┘  └───────┬────────┘  └─────────┬──────────┘   │
│         │                  │                      │              │
│         └──────────────────┴──────────────────────┘              │
│                              │                                   │
│                              ▼                                   │
│              ┌────────────────────────────┐                      │
│              │  🛠️ Gestor de Herramientas  │                      │
│              └────────────────────────────┘                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAPA DE DOMINIO — HERRAMIENTAS                      │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ get_clima_   │  │get_pronostico│  │ evaluar_operacion    │   │
│  │ actual       │  │_semana       │  │                      │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                 │                      │              │
│         ▼                 ▼                      ▼              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              API Open-Meteo (gratuita, sin key)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              FAISS Vector Store (RAG)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAPA DE INFRAESTRUCTURA                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   GitHub     │  │   LangSmith  │  │  AWS EC2 (Caddy +    │   │
│  │ Models API   │  │   Tracing    │  │  Docker)             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```
""")

    st.markdown("---")
    st.markdown("### 🧠 Componentes Clave")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### LangGraph (ReAct)")
        st.markdown("""
        - Ciclo **Razonar → Actuar → Observar**
        - Nativo en LangChain 1.3+
        - Manejo de herramientas con @tool decorator
        """)
        st.markdown("#### CrewAI (Multi-Agente)")
        st.markdown("""
        - **Meteorólogo Acuícola**: clima y pronóstico
        - **Coordinador Operaciones**: planificación
        - **Supervisor General**: reporte ejecutivo
        """)
    with col2:
        st.markdown("#### Memoria Conversacional")
        st.markdown("""
        - `InMemoryChatMessageHistory`: sesiones
        - `ConversationBufferMemory`: historial completo
        - `ConversationWindowMemory`: ventana k=2
        - `ConversationSummaryMemory`: resumen automático
        """)
        st.markdown("#### RAG con FAISS")
        st.markdown("""
        - Embeddings: `text-embedding-3-small`
        - Chunk size: 400, overlap: 60
        - Retrieve: top-k=2 por consulta
        """)

elif pagina == "Observabilidad":
    st.markdown('<p class="main-header">📊 Observabilidad y Métricas</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">IL3.1 / IE9 — Precisión, Latencia y Consistencia</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latencia Promedio", "4,253 ms", "±10.75% CV")
        st.metric("Precisión", "80%", "Resp. con datos numéricos")
    with col2:
        st.metric("Tasa de Éxito", "100%", "Sin errores")
        st.metric("Tokens Totales", "302", "5 consultas")

    if os.path.exists("dashboard_observabilidad_camanchaca.png"):
        st.image("dashboard_observabilidad_camanchaca.png", caption="Dashboard de Observabilidad — Latencia y Precisión por Consulta", use_container_width=True)
    else:
        st.info("Dashboard no disponible - ejecuta IA_agente_Camanchaca5.ipynb para generarlo")

    st.markdown("---")
    st.markdown("### 🔍 Trazabilidad (IL3.2 / IE10)")
    st.markdown("""
    - **Trace ID único** por consulta (UUID)
    - **3 etapas**: validación de entrada → identificación de centro → invocación del agente
    - **Analizador de trazas**: identifica etapa más lenta y puntos de falla
    - **Formato JSON estructurado** para auditoría

    **Hallazgos:**
    - La etapa `invocacion_agente` concentra >90% de la latencia (~3.8s)
    - Mensajes vacíos generan trazas con error (validación temprana agregada)
    """)

elif pagina == "Seguridad":
    st.markdown('<p class="main-header">🔒 Seguridad y Uso Responsable</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">IL3.3 / IE11 — Guardrails, Ética y Privacidad</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Pipeline de Seguridad")
    st.markdown("""
    1. **Rate Limiting** → 10 peticiones/minuto (límite GitHub Models)
    2. **Anti-Prompt Injection** → 6 patrones regex bloqueados
    3. **Filtro Ético** → 3 categorías: seguridad infraestructura, manipulación datos, riesgo laboral
    4. **Sanitización de PII** → Correos, RUT chilenos, teléfonos redactados
    5. **Invocación del Agente** → Solo si pasa todos los filtros
    """)

    st.markdown("---")
    st.markdown("### Checklist OWASP LLM Top 10 (IL3.5)")
    items = [
        ("Prompt Injection bloqueado", "✅"),
        ("Rate limiting (429 en exceso)", "✅"),
        ("PII redactada en respuestas y logs", "✅"),
        ("Errores sin exponer trazas internas", "✅"),
        ("Validación de parámetros antes de APIs externas", "✅"),
        ("HTTPS obligatorio (Caddy)", "✅"),
        ("Contenedores no-root", "✅"),
        ("Security Group restrictivo", "✅"),
    ]
    for desc, estado in items:
        st.markdown(f"- {estado} {desc}")

elif pagina == "Despliegue":
    st.markdown('<p class="main-header">☁️ Despliegue en AWS</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">IL3.5 — Ciberseguridad y Despliegue en AWS Academy</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Arquitectura de Despliegue")
    st.markdown("""
    ```
    ┌────────────────────────────────────────────────────┐
    │              EC2 (Amazon Linux 2023, t3.small)       │
    │                                                       │
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
    ```
    """)

    st.markdown("### Pasos de Despliegue (AWS Academy)")
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
        st.markdown(f"{i}. {paso}")
