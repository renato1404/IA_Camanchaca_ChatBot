#!/usr/bin/env python3
"""IA Camanchaca ChatBot - CLI Agent (refactored)
Monitoreo climático para Salmones Camanchaca.
Ejecutar: python bot.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from clima_utils import (
    get_clima_actual as _get_clima,
    get_pronostico_semana as _get_pronos,
    formatear_clima,
    formatear_pronostico,
)

load_dotenv()

if not os.getenv("OPENAI_BASE_URL") or not os.getenv("GITHUB_TOKEN"):
    raise ValueError("Falta OPENAI_BASE_URL o GITHUB_TOKEN en .env")

@tool
def get_clima_actual(centro: str) -> str:
    """Obtiene el clima actual con temperatura, humedad relativa, viento (velocidad y dirección cardinal N/S/E/O), índice UV con nivel de riesgo, precipitación, probabilidad de precipitación y horas de sol. Parámetro: ensenada, puelche o huito."""
    return formatear_clima(_get_clima(centro))

@tool
def get_pronostico_semana(centro: str) -> str:
    """Obtiene el pronóstico de 7 días con temperatura min/max, viento, lluvia, probabilidad de precipitación, dirección del viento dominante en formato cardinal (N/S/E/O) y horas de salida/puesta del sol. Parámetro: ensenada, puelche o huito."""
    return formatear_pronostico(_get_pronos(centro))

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
    model="gpt-4o",
    temperature=0,
    request_timeout=600,
)

agent = create_react_agent(llm, [get_clima_actual, get_pronostico_semana])

def main():
    print("=" * 50)
    print("IA Camanchaca ChatBot - Agente Climático")
    print("Centros: Ensenada, Puelche, Huito")
    print("Escribe 'salir' para terminar")
    print("=" * 50)
    while True:
        try:
            query = input("\nTu consulta: ").strip()
            if not query:
                continue
            if query.lower() in ("salir", "exit", "quit"):
                print("¡Hasta luego!")
                break
            response = agent.invoke({"messages": [("human", query)]})
            print(f"\nRespuesta: {response['messages'][-1].content}")
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
