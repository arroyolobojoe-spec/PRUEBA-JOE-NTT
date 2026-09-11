"""
Chatbot de consulta en lenguaje natural sobre el analisis de consumo domestico de cafe
(High Garden Coffee). Lee el resumen de datos ya calculado por el notebook principal
(../outputs/analysis_summary.json) y responde preguntas del usuario.

Dos modos:
- Modo LLM real: si la variable de entorno ANTHROPIC_API_KEY esta definida (o existe un
  archivo .env local con ANTHROPIC_API_KEY=...), usa el SDK oficial de Anthropic con
  tool-use: el modelo elige que funcion de consulta ejecutar sobre los datos y redacta
  la respuesta final en lenguaje natural citando las cifras.
- Modo mock/dry-run: si no hay API key configurada, entra en un menu interactivo de
  preguntas frecuentes precanned, respondidas directamente desde los datos (sin LLM),
  para que el script sea ejecutable de inmediato sin credenciales externas.

Uso:
    python chatbot.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
SUMMARY_PATH = BASE_DIR.parent / "outputs" / "analysis_summary.json"


def load_summary() -> dict:
    if not SUMMARY_PATH.exists():
        print(f"No se encontro {SUMMARY_PATH}.")
        print("Ejecuta primero el notebook analisis_coffee_high_garden.ipynb para generarlo.")
        sys.exit(1)
    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Funciones de consulta sobre el resumen de datos (usadas como "tools" del LLM
# y tambien directamente en modo mock). Deliberadamente son consultas acotadas
# y seguras sobre datos precalculados, no ejecucion de codigo arbitrario.
# ---------------------------------------------------------------------------

def get_country_stats(summary: dict, country: str) -> dict:
    country = country.strip().lower()
    for c in summary["countries"]:
        if c["country"].lower() == country or country in c["country"].lower():
            return c
    return {"error": f"No se encontro el pais '{country}' en el dataset."}


def get_top_growth(summary: dict, n: int = 5, ascending: bool = False) -> list:
    rows = [c for c in summary["countries"] if c["cagr"] is not None]
    rows.sort(key=lambda c: c["cagr"], reverse=not ascending)
    return rows[:n]


def get_cluster_info(summary: dict, country: str | None = None) -> dict:
    if country:
        country = country.strip().lower()
        for c in summary["countries"]:
            if c["country"].lower() == country or country in c["country"].lower():
                cluster_id = c["cluster"]
                return {
                    "country": c["country"],
                    "cluster": cluster_id,
                    "cluster_profile": summary["clusters"].get(str(cluster_id), {}),
                }
        return {"error": f"No se encontro el pais '{country}' en el dataset."}
    return summary["clusters"]


def get_forecast(summary: dict, entity: str = "global") -> dict:
    entity_key = entity.strip().lower()
    forecasts = summary["forecast"]
    if entity_key in forecasts:
        return forecasts[entity_key]
    for key in forecasts:
        if entity_key in key.lower():
            return forecasts[key]
    return {"error": f"No hay forecast disponible para '{entity}'.", "disponibles": list(forecasts.keys())}


def get_price_index(summary: dict) -> dict:
    return summary.get("price_index", {"error": "No hay indice de precios simulado en el resumen."})


TOOLS_SPEC = [
    {
        "name": "get_country_stats",
        "description": "Obtiene estadisticas de consumo domestico de cafe de un pais especifico: total historico, CAGR, tipo de cafe, cluster asignado.",
        "input_schema": {
            "type": "object",
            "properties": {"country": {"type": "string", "description": "Nombre del pais (en espanol o ingles, coincidencia parcial permitida)"}},
            "required": ["country"],
        },
    },
    {
        "name": "get_top_growth",
        "description": "Obtiene el ranking de paises con mayor (o menor) crecimiento de consumo domestico (CAGR 1990/91-2019/20).",
        "input_schema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Cantidad de paises a devolver, por defecto 5"},
                "ascending": {"type": "boolean", "description": "true para obtener los de menor crecimiento (declive), false (default) para mayor crecimiento"},
            },
        },
    },
    {
        "name": "get_cluster_info",
        "description": "Obtiene el perfil de los segmentos (clusters) de paises productores, o el cluster de un pais especifico si se indica.",
        "input_schema": {
            "type": "object",
            "properties": {"country": {"type": "string", "description": "Nombre del pais (opcional). Si se omite, devuelve el perfil de todos los clusters."}},
        },
    },
    {
        "name": "get_forecast",
        "description": "Obtiene el forecast de consumo domestico proyectado (2020/21-2024/25) para 'global', un tipo de cafe ('arabica', 'robusta', 'mixto') o un pais del top 10.",
        "input_schema": {
            "type": "object",
            "properties": {"entity": {"type": "string", "description": "Entidad a consultar: 'global', un tipo de cafe, o un pais del top 10 por consumo"}},
            "required": ["entity"],
        },
    },
    {
        "name": "get_price_index",
        "description": "Obtiene el indice de presion de precios SIMULADO (proxy ilustrativo, no datos de mercado reales) y su rango proyectado a futuro.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

TOOL_FUNCS = {
    "get_country_stats": get_country_stats,
    "get_top_growth": get_top_growth,
    "get_cluster_info": get_cluster_info,
    "get_forecast": get_forecast,
    "get_price_index": get_price_index,
}


def run_llm_mode(summary: dict, api_key: str) -> None:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = (
        "Eres un analista de datos para High Garden Coffee, una exportadora internacional de "
        "cafe. Respondes preguntas sobre el consumo domestico historico de cafe (1990-2020), "
        "crecimiento por pais, segmentacion de mercados y forecasts, usando EXCLUSIVAMENTE los "
        "datos que obtengas de las herramientas disponibles. Si el indice de precios es "
        "consultado, aclara siempre que es una simulacion ilustrativa y no un dato de mercado "
        "real. Responde en espanol, de forma breve y citando cifras concretas."
    )
    print("Chatbot High Garden Coffee (modo LLM real, Claude). Escribe 'salir' para terminar.\n")
    while True:
        try:
            question = input("Pregunta> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question or question.lower() in {"salir", "exit", "quit"}:
            break

        messages = [{"role": "user", "content": question}]
        while True:
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                system=system_prompt,
                tools=TOOLS_SPEC,
                messages=messages,
            )
            if response.stop_reason != "tool_use":
                for block in response.content:
                    if block.type == "text":
                        print(f"\n{block.text}\n")
                break

            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                func = TOOL_FUNCS[block.name]
                try:
                    result = func(summary, **block.input)
                except TypeError:
                    result = func(summary)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
            messages.append({"role": "user", "content": tool_results})


MOCK_QUESTIONS = [
    ("Top 5 paises con mayor crecimiento de consumo domestico", lambda s: get_top_growth(s, 5, False)),
    ("Top 5 paises con menor crecimiento (o en declive)", lambda s: get_top_growth(s, 5, True)),
    ("Perfil de todos los segmentos (clusters) de paises", lambda s: get_cluster_info(s)),
    ("Forecast global de consumo domestico 2020/21-2024/25", lambda s: get_forecast(s, "global")),
    ("Indice de presion de precios simulado", lambda s: get_price_index(s)),
    ("Consultar un pais especifico (Brazil, Colombia, Viet Nam, ...)", None),
]


def run_mock_mode(summary: dict) -> None:
    print("=" * 70)
    print("Chatbot High Garden Coffee (MODO MOCK / DRY-RUN)")
    print("No se detecto ANTHROPIC_API_KEY en el entorno ni en un archivo .env local,")
    print("asi que este modo responde con datos precalculados, sin llamar a un LLM.")
    print("Para el modo con LLM real, define ANTHROPIC_API_KEY y vuelve a ejecutar.")
    print("=" * 70)

    while True:
        print("\nPreguntas disponibles:")
        for i, (label, _) in enumerate(MOCK_QUESTIONS, start=1):
            print(f"  {i}. {label}")
        print("  0. Salir")

        choice = input("\nElige una opcion (numero)> ").strip()
        if choice == "0" or choice.lower() in {"salir", "exit", "quit"}:
            break
        try:
            idx = int(choice) - 1
            label, func = MOCK_QUESTIONS[idx]
        except (ValueError, IndexError):
            print("Opcion invalida, intenta de nuevo.")
            continue

        if func is None:
            country = input("Nombre del pais> ").strip()
            result = get_country_stats(summary, country)
        else:
            result = func(summary)

        print(f"\n--- {label} ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    summary = load_summary()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        run_llm_mode(summary, api_key)
    else:
        run_mock_mode(summary)


if __name__ == "__main__":
    main()
