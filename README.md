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