import os, re, requests
from functools import lru_cache
from datetime import datetime, timedelta

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

def _get_cache_buster():
    return datetime.now().strftime("%H")

@lru_cache(maxsize=8)
def _fetch_atmosfera(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,weathercode,uv_index"
           f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,weathercode"
           f"&timezone=America/Santiago")
    return requests.get(url, timeout=10).json()

@lru_cache(maxsize=8)
def _fetch_marino(lat, lon):
    url = (f"https://marine-api.open-meteo.com/v1/marine"
           f"?latitude={lat}&longitude={lon}"
           f"&current=wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction"
           f"&daily=water_temperature_2m_max,water_temperature_2m_min"
           f"&timezone=America/Santiago")
    return requests.get(url, timeout=10).json()

def get_clima_actual(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    try:
        _get_cache_buster()
        r = _fetch_atmosfera(d["lat"], d["lon"])["current"]
        return {
            "centro": d["nombre"],
            "region": d["region"],
            "temp": r["temperature_2m"],
            "humedad": r.get("relative_humidity_2m"),
            "viento": r["wind_speed_10m"],
            "viento_dir": r.get("wind_direction_10m"),
            "lluvia": r["precipitation"],
            "uv": r.get("uv_index"),
            "codigo": r["weathercode"],
            "condicion": CODIGOS_CLIMA(r["weathercode"]),
        }
    except Exception as e:
        return {"error": f"Error al obtener datos: {e}"}

def get_pronostico_semana(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    try:
        _get_cache_buster()
        r = _fetch_atmosfera(d["lat"], d["lon"])["daily"]
        dias = []
        for i in range(7):
            dias.append({
                "fecha": r["time"][i],
                "tmax": r["temperature_2m_max"][i],
                "tmin": r["temperature_2m_min"][i],
                "lluvia": r["precipitation_sum"][i],
                "prob_lluvia": r.get("precipitation_probability_max", [None])[i] if r.get("precipitation_probability_max") else None,
                "viento": r["wind_speed_10m_max"][i],
                "condicion": CODIGOS_CLIMA(r["weathercode"][i]),
            })
        return {"centro": d["nombre"], "dias": dias}
    except Exception as e:
        return {"error": f"Error: {e}"}

def get_condiciones_marinas(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    try:
        _get_cache_buster()
        r = _fetch_marino(d["lat"], d["lon"])["current"]
        daily = _fetch_marino(d["lat"], d["lon"]).get("daily", {})
        agua_max = daily.get("water_temperature_2m_max", [None])[0] if daily.get("water_temperature_2m_max") else None
        agua_min = daily.get("water_temperature_2m_min", [None])[0] if daily.get("water_temperature_2m_min") else None
        return {
            "centro": d["nombre"],
            "ola_altura": r.get("wave_height"),
            "ola_direccion": r.get("wave_direction"),
            "ola_periodo": r.get("wave_period"),
            "swell_altura": r.get("swell_wave_height"),
            "swell_direccion": r.get("swell_wave_direction"),
            "agua_temp_max": agua_max,
            "agua_temp_min": agua_min,
        }
    except Exception as e:
        return {"error": f"Error al obtener datos marinos: {e}"}

DIRECCIONES_VIENTO = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]

def viento_dir_texto(grados):
    if grados is None:
        return None
    idx = round(grados / 22.5) % 16
    return DIRECCIONES_VIENTO[idx]

def formatear_clima(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    lineas = [f"Centro: {datos['centro']}", f"Temperatura: {datos['temp']}°C"]
    if datos.get("humedad") is not None:
        lineas.append(f"Humedad: {datos['humedad']}%")
    lineas.append(f"Viento: {datos['viento']} km/h")
    dir_texto = viento_dir_texto(datos.get("viento_dir"))
    if dir_texto:
        lineas[-1] += f" ({dir_texto})"
    lineas.append(f"Precipitación: {datos['lluvia']} mm")
    if datos.get("uv") is not None:
        lineas.append(f"Índice UV: {datos['uv']}")
    lineas.append(f"Condición: {datos['condicion']}")
    return "\n".join(lineas)

def formatear_pronostico(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    r = f"Pronóstico 7 días - {datos['centro']}:\n"
    for d in datos["dias"]:
        prob = f" | Prob. lluvia: {d['prob_lluvia']}%" if d.get("prob_lluvia") is not None else ""
        r += (f"\n{d['fecha']}: {d['tmin']}°C-{d['tmax']}°C | "
              f"Viento: {d['viento']} km/h | Lluvia: {d['lluvia']} mm{prob} | {d['condicion']}")
    return r

def formatear_marino(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    lineas = [f"Condiciones marinas - {datos['centro']}"]
    if datos.get("ola_altura") is not None:
        lineas.append(f"Altura de ola: {datos['ola_altura']} m")
    if datos.get("ola_periodo") is not None:
        lineas.append(f"Período de ola: {datos['ola_periodo']} s")
    if datos.get("swell_altura") is not None:
        lineas.append(f"Altura de swell: {datos['swell_altura']} m")
    if datos.get("agua_temp_max") is not None:
        lineas.append(f"Temp. agua superficial: {datos['agua_temp_min']}°C-{datos['agua_temp_max']}°C")
    return "\n".join(lineas)
