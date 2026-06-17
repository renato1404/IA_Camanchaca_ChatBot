#!/usr/bin/env python3
"""IA Camanchaca ChatBot - CLI Agent
Monitoreo climatico para Salmones Camanchaca.
Ejecutar: python bot.py
"""

import os
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

if not os.getenv("OPENAI_BASE_URL") or not os.getenv("GITHUB_TOKEN"):
    raise ValueError("Falta OPENAI_BASE_URL o GITHUB_TOKEN en .env")

CENTROS = {
    "ensenada": {"lat": -41.140459, "lon": -72.404236, "nombre": "Piscicultura Petrohue"},
    "puelche":  {"lat": -41.733,    "lon": -73.602,    "nombre": "Centro Puelche"},
    "huito":    {"lat": -41.783,    "lon": -73.583,    "nombre": "Centro Huito (San Jose)"},
}

@tool
def get_clima_actual(centro: str) -> str:
    """Obtiene el clima actual para un centro de cultivo. Parametro: ensenada, puelche o huito."""
    if centro.lower() not in CENTROS:
        return f"Centro '{centro}' no encontrado. Opciones: ensenada, puelche, huito."
    datos = CENTROS[centro.lower()]
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={datos['lat']}&longitude={datos['lon']}"
        f"&current=temperature_2m,wind_speed_10m,precipitation,weathercode"
        f"&timezone=America/Santiago"
    )
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        current = data["current"]
        temp = current["temperature_2m"]
        viento = current["wind_speed_10m"]
        lluvia = current["precipitation"]
        codigo = current["weathercode"]
        condicion = "Despejado" if codigo < 3 else "Nublado" if codigo < 50 else "Lluvia"
        return (f"Centro: {datos['nombre']}\nTemperatura: {temp}C\n"
                f"Viento: {viento} km/h\nPrecipitacion: {lluvia} mm\nCondicion: {condicion}")
    except Exception as e:
        return f"Error al obtener datos: {e}"

@tool
def get_pronostico_semana(centro: str) -> str:
    """Obtiene el pronostico de 7 dias. Parametro: ensenada, puelche o huito."""
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
        resultado = f"Pronostico 7 dias - {datos['nombre']}:\n"
        for i in range(7):
            fecha = daily["time"][i]
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            lluvia = daily["precipitation_sum"][i]
            viento = daily["wind_speed_10m_max"][i]
            codigo = daily["weathercode"][i]
            condicion = "Despejado" if codigo < 3 else "Nublado" if codigo < 50 else "Lluvia"
            resultado += f"\n{fecha}: {tmin}C-{tmax}C | Viento: {viento} km/h | Lluvia: {lluvia} mm | {condicion}"
        return resultado
    except Exception as e:
        return f"Error: {e}"

tools = [get_clima_actual, get_pronostico_semana]

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("GITHUB_TOKEN"),
    model="gpt-4o",
    temperature=0,
    request_timeout=600,
)

agent = create_react_agent(llm, tools)

def main():
    print("=" * 50)
    print("IA Camanchaca ChatBot - Agente Climatico")
    print("Centros: Ensenada, Puelche, Huito")
    print("Escribe 'salir' para terminar")
    print("=" * 50)
    while True:
        try:
            query = input("\nTu consulta: ").strip()
            if not query:
                continue
            if query.lower() in ("salir", "exit", "quit"):
                print("Hasta luego!")
                break
            response = agent.invoke({"messages": [("human", query)]})
            print(f"\nRespuesta: {response['messages'][-1].content}")
        except KeyboardInterrupt:
            print("\nHasta luego!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
