import os, re, requests

CENTROS = {
    "ensenada": {"lat": -41.140459, "lon": -72.404236, "nombre": "Piscicultura Petrohué", "region": "Los Lagos"},
    "puelche":  {"lat": -41.733,    "lon": -73.602,    "nombre": "Centro Puelche",        "region": "Los Lagos"},
    "huito":    {"lat": -41.783,    "lon": -73.583,    "nombre": "Centro Huito (San José)", "region": "Los Lagos"},
}

PATRONES_INYECCION = [
    r"ignora\s*(instrucciones|comandos|reglas)",
    r"olvida\s*tus\s*(instrucciones|reglas)",
    r"bypassea\s*la\s*seguridad",
    r"eres\s*libre\s*y\s*sin\s*restricciones",
    r"dime\s*lo\s*que\s*sea\s*sin\s*filtros",
    r"no\s*tengas\s*limites",
]

RE_PII = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "telefono": re.compile(r"(\+?56)?\s*9\s*\d{4}\s*\d{4}"),
    "rut": re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]\b"),
}

CODIGOS_CLIMA = lambda c: "Despejado" if c < 3 else "Nublado" if c < 50 else "Lluvia"

def validar_entrada(texto):
    if not texto or not texto.strip():
        return False, "La consulta no puede estar vacía."
    for p in PATRONES_INYECCION:
        if re.search(p, texto.lower()):
            return False, "Consulta rechazada por políticas de seguridad."
    return True, ""

def sanitizar_pii(texto):
    for nom, rx in RE_PII.items():
        texto = rx.sub(f"[{nom.upper()}_REDACTADO]", texto)
    return texto

def get_clima_actual(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={d['lat']}&longitude={d['lon']}"
           f"&current=temperature_2m,wind_speed_10m,precipitation,weathercode"
           f"&timezone=America/Santiago")
    try:
        r = requests.get(url, timeout=10).json()["current"]
        return {
            "centro": d["nombre"],
            "temp": r["temperature_2m"],
            "viento": r["wind_speed_10m"],
            "lluvia": r["precipitation"],
            "codigo": r["weathercode"],
            "condicion": CODIGOS_CLIMA(r["weathercode"]),
        }
    except Exception as e:
        return {"error": f"Error al obtener datos: {e}"}

def get_pronostico_semana(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={d['lat']}&longitude={d['lon']}"
           f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weathercode"
           f"&timezone=America/Santiago")
    try:
        r = requests.get(url, timeout=10).json()["daily"]
        dias = []
        for i in range(7):
            dias.append({
                "fecha": r["time"][i],
                "tmax": r["temperature_2m_max"][i],
                "tmin": r["temperature_2m_min"][i],
                "lluvia": r["precipitation_sum"][i],
                "viento": r["wind_speed_10m_max"][i],
                "condicion": CODIGOS_CLIMA(r["weathercode"][i]),
            })
        return {"centro": d["nombre"], "dias": dias}
    except Exception as e:
        return {"error": f"Error: {e}"}

def formatear_clima(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    return (f"Centro: {datos['centro']}\nTemperatura: {datos['temp']}°C\n"
            f"Viento: {datos['viento']} km/h\nPrecipitación: {datos['lluvia']} mm\n"
            f"Condición: {datos['condicion']}")

def formatear_pronostico(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    r = f"Pronóstico 7 días - {datos['centro']}:\n"
    for d in datos["dias"]:
        r += (f"\n{d['fecha']}: {d['tmin']}°C-{d['tmax']}°C | "
              f"Viento: {d['viento']} km/h | Lluvia: {d['lluvia']} mm | {d['condicion']}")
    return r
