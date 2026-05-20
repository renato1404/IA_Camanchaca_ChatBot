# IA_Camanchaca_ChatBot
ChatBot asistente de IA para empresa salmonera Camanchaca, prueba ingenieria en soluciones con IA

1. ¿Cómo se ajustó la estructura de los prompts para cumplir con los requerimientos informacionales? (IL 1.1)
Los prompts fueron diseñados bajo una arquitectura de Few-Shot Progresivo y Chain-of-Thought (CoT):

Contextualización: Se utilizaron raw strings (r''') para asegurar que las expresiones regulares complejas (como validaciones de email o teléfonos chilenos) no fueran alteradas por el intérprete de Python, garantizando precisión técnica.
Ejemplificación (Few-Shot): Se incluyeron ejemplos de menor a mayor complejidad para "guiar" al modelo en la generación de respuestas con un formato consistente de "Regex + Explicación".
Estructuración de Razonamiento (CoT): En tareas críticas como el debugging, se forzó al modelo a seguir una secuencia lógica (Comprensión -> Análisis -> Identificación -> Solución) antes de entregar el resultado final, reduciendo errores lógicos.

2. ¿De qué manera el flujo implementado enriquece las respuestas del modelo? (IL 1.2)
El flujo enriquece la experiencia del usuario y la calidad del dato mediante dos mecanismos clave:

Streaming de Datos: Permite una interacción dinámica al visualizar la construcción de la respuesta en tiempo real, lo cual es esencial en contextos organizacionales para mejorar la percepción de velocidad y transparencia del sistema.
Control de Contexto (Memoria): La integración de ConversationBufferMemory permite que el modelo "recuerde" interacciones previas. Esto enriquece la respuesta actual al permitir referencias cruzadas (ej. aplicar un estilo de programación sugerido en un paso anterior a una nueva tarea de debugging).

3. Justificación de la Arquitectura de Solución (IL 1.3 e IL 1.4)
La arquitectura propuesta integra componentes de LangChain para maximizar la trazabilidad y relevancia:

Módulo de Generación: Se utiliza un modelo con temperatura baja (0.1) para asegurar respuestas deterministas y técnicas, ideales para la generación de código y expresiones regulares.Módulo de Control: La memoria actúa como un filtro de relevancia, asegurando que las respuestas se mantengan dentro del dominio organizacional definido en el historial de la conversación.Módulo de Entrega: El streaming desacopla la generación del procesamiento final, permitiendo una entrega de información fluida y coherente con las expectativas de un sistema de asistencia técnica.

4. Limitaciones y Consideraciones Técnicas

Trazabilidad: Al documentar el proceso de pensamiento (CoT), se cumple con el requerimiento de justificar técnicamente cada decisión de diseño, permitiendo auditorías de cómo la IA llegó a una conclusión específica.Validación Humana: Siguiendo las instrucciones éticas del encargo, toda respuesta generada (especialmente el código de debugging) debe ser validada por el equipo antes de su implementación final en un entorno real.


# 🐟 IA_Camanchaca_ChatBot - Sistema de Agentes para Monitoreo Climático y Operacional

[cite_start]Este repositorio digital contiene el desarrollo e implementación de un sistema de agentes funcionales e inteligentes diseñado para **Salmones Camanchaca**. [cite_start]El objetivo principal de la solución es automatizar el monitoreo de las condiciones climáticas y oceanográficas en tiempo real en los centros de cultivo de la Región de Los Lagos (**Ensenada/Piscicultura Petrohué, Puelche y Huito**), interactuando de forma autónoma con APIs externas y bases de datos documentales para mitigar riesgos operativos y optimizar la toma de decisiones[cite: 9, 10, 24].

---

## 🏗️ Arquitectura General y Orquestación

[cite_start]El sistema está diseñado bajo una arquitectura modular y desacoplada utilizando **LangChain** y **CrewAI**, permitiendo que los agentes razonen, planifiquen y ejecuten herramientas de consulta de forma autónoma.

```mermaid
graph TD
    User([👤 Operador Camanchaca]) -->|Consulta en Lenguaje Natural| MainAgent[🤖 Agente Operacional Principal]
    
    subgraph Framework de Agentes (LangChain / CrewAI)
        MainAgent -->|Razonamiento / ReAct| ToolManager{🛠️ Gestor de Herramientas}
        MainAgent -->|Memoria Corto Plazo| ChatHistory[(💬 Historial de Chat)]
    end
    
    subgraph Herramientas e Integraciones Externas
        ToolManager -->|Consulta coordenadas| WeatherAPI[🌤️ API Open-Meteo]
        ToolManager -->|Búsqueda Semántica| RAG[📚 Base de Vectores FAISS]
    end
    
    WeatherAPI -->|Datos de clima actuales y pronósticos| MainAgent
    RAG -->|Protocolos de umbrales críticos y normativas| MainAgent
    MainAgent -->|Evaluación Operativa Adaptativa| User