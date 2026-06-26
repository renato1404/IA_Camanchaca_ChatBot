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
DIR_16 = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
DIR_4 = ["N","E","S","W"]

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

def dir_a_texto(grados):
    if grados is None:
        return None
    return DIR_16[round(grados / 22.5) % 16]

def dir_a_cardinal(grados):
    if grados is None:
        return None
    return DIR_4[round(grados / 90) % 4]

def uv_nivel(valor):
    if valor is None:
        return None
    if valor < 3:
        return "Bajo"
    if valor < 6:
        return "Moderado"
    if valor < 8:
        return "Alto"
    if valor < 11:
        return "Muy alto"
    return "Extremo"

@lru_cache(maxsize=8)
def _fetch_atmosfera(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,weathercode,uv_index"
           f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant,weathercode,sunrise,sunset"
           f"&timezone=America/Santiago"
           f"&forecast_days=7")
    return requests.get(url, timeout=10).json()

@lru_cache(maxsize=8)
def _fetch_marino(lat, lon):
    url = (f"https://marine-api.open-meteo.com/v1/marine"
           f"?latitude={lat}&longitude={lon}"
           f"&current=wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period,water_temperature_2m"
           f"&daily=water_temperature_2m_max,water_temperature_2m_min"
           f"&timezone=America/Santiago"
           f"&forecast_days=7")
    return requests.get(url, timeout=10).json()

def get_clima_actual(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    try:
        data = _fetch_atmosfera(d["lat"], d["lon"])
        r = data["current"]
        daily = data.get("daily", {})
        return {
            "centro": d["nombre"], "region": d["region"],
            "temp": r["temperature_2m"],
            "humedad": r.get("relative_humidity_2m"),
            "viento": r["wind_speed_10m"],
            "viento_dir": r.get("wind_direction_10m"),
            "lluvia": r["precipitation"],
            "uv": r.get("uv_index"),
            "codigo": r["weathercode"],
            "condicion": CODIGOS_CLIMA(r["weathercode"]),
            "prob_lluvia": (daily.get("precipitation_probability_max") or [None])[0],
            "sunrise": (daily.get("sunrise") or [""])[0],
            "sunset": (daily.get("sunset") or [""])[0],
        }
    except Exception as e:
        return {"error": f"Error al obtener datos: {e}"}

def get_pronostico_semana(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    try:
        r = _fetch_atmosfera(d["lat"], d["lon"])["daily"]
        dias = []
        for i in range(7):
            dias.append({
                "fecha": r["time"][i],
                "tmax": r["temperature_2m_max"][i],
                "tmin": r["temperature_2m_min"][i],
                "lluvia": r["precipitation_sum"][i],
                "prob_lluvia": (r.get("precipitation_probability_max") or [None])[i],
                "viento": r["wind_speed_10m_max"][i],
                "viento_dom": (r.get("wind_direction_10m_dominant") or [None])[i],
                "condicion": CODIGOS_CLIMA(r["weathercode"][i]),
                "sunrise": r.get("sunrise", [""])[i] if r.get("sunrise") else "",
                "sunset": r.get("sunset", [""])[i] if r.get("sunset") else "",
            })
        return {"centro": d["nombre"], "dias": dias}
    except Exception as e:
        return {"error": f"Error: {e}"}

def get_condiciones_marinas(centro: str) -> dict:
    if centro.lower() not in CENTROS:
        return {"error": f"Centro '{centro}' no encontrado."}
    d = CENTROS[centro.lower()]
    try:
        r = _fetch_marino(d["lat"], d["lon"])["current"]
        daily = _fetch_marino(d["lat"], d["lon"]).get("daily", {})
        return {
            "centro": d["nombre"],
            "temp_agua": r.get("water_temperature_2m"),
            "agua_temp_max": (daily.get("water_temperature_2m_max") or [None])[0],
            "agua_temp_min": (daily.get("water_temperature_2m_min") or [None])[0],
            "ola_altura": r.get("wave_height"),
            "ola_direccion": r.get("wave_direction"),
            "ola_periodo": r.get("wave_period"),
            "swell_altura": r.get("swell_wave_height"),
            "swell_direccion": r.get("swell_wave_direction"),
            "swell_periodo": r.get("swell_wave_period"),
        }
    except Exception as e:
        return {"error": f"Error al obtener datos marinos: {e}"}

def formatear_clima(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    lineas = [f"Centro: {datos['centro']}", f"Temperatura: {datos['temp']}°C"]
    if datos.get("humedad") is not None:
        lineas.append(f"Humedad: {datos['humedad']}%")
    v = f"Viento: {datos['viento']} km/h"
    d16 = dir_a_texto(datos.get("viento_dir"))
    d4 = dir_a_cardinal(datos.get("viento_dir"))
    if d4: v += f" {d4} ({d16})"
    lineas.append(v)
    lineas.append(f"Precipitación: {datos['lluvia']} mm")
    if datos.get("prob_lluvia") is not None:
        lineas.append(f"Probabilidad de precipitación: {datos['prob_lluvia']}%")
    if datos.get("uv") is not None:
        nivel = uv_nivel(datos["uv"])
        lineas.append(f"Índice UV: {datos['uv']} ({nivel})")
    if datos.get("sunrise"):
        lineas.append(f"Sol: {datos['sunrise'][-5:]} – {datos['sunset'][-5:]}")
    lineas.append(f"Condición: {datos['condicion']}")
    return "\n".join(lineas)

def formatear_pronostico(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    r = f"Pronóstico 7 días - {datos['centro']}:\n"
    for d in datos["dias"]:
        extras = []
        if d.get("prob_lluvia") is not None: extras.append(f"Prob. lluvia: {d['prob_lluvia']}%")
        v_dir = dir_a_cardinal(d.get("viento_dom"))
        if v_dir: extras.append(f"Viento {v_dir}")
        if d.get("sunrise"): extras.append(f"Sol: {d['sunrise'][-5:]}‑{d['sunset'][-5:]}")
        extra = f" | {', '.join(extras)}" if extras else ""
        r += (f"\n{d['fecha']}: {d['tmin']}°C-{d['tmax']}°C | "
              f"Viento: {d['viento']} km/h | Lluvia: {d['lluvia']} mm{extra} | {d['condicion']}")
    return r

def formatear_marino(datos: dict) -> str:
    if "error" in datos:
        return datos["error"]
    lineas = [f"Condiciones marinas - {datos['centro']}"]
    if datos.get("temp_agua") is not None:
        lineas.append(f"Temperatura del agua superficial: {datos['temp_agua']}°C")
    if datos.get("agua_temp_max") is not None:
        lineas.append(f"Rango temp. agua: {datos['agua_temp_min']}°C-{datos['agua_temp_max']}°C")
    if datos.get("ola_altura") is not None:
        d = dir_a_texto(datos.get("ola_direccion"))
        lineas.append(f"Ola: {datos['ola_altura']} m" + (f" ({d})" if d else ""))
    if datos.get("ola_periodo") is not None:
        lineas.append(f"Período de ola: {datos['ola_periodo']} s")
    if datos.get("swell_altura") is not None:
        d = dir_a_texto(datos.get("swell_direccion"))
        lineas.append(f"Swell: {datos['swell_altura']} m" + (f" ({d})" if d else ""))
    if datos.get("swell_periodo") is not None:
        lineas.append(f"Período swell: {datos['swell_periodo']} s")
    return "\n".join(lineas)
