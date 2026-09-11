Chatbot High Garden Coffee - instrucciones

Que es

Script de linea de comandos que permite hacer preguntas en lenguaje natural sobre el
analisis de consumo domestico de cafe (tendencias, crecimiento por pais, clusters,
forecast, indice de precios simulado). Usa un patron de tool-use: el modelo Claude elige
que funcion de consulta ejecutar sobre los datos ya calculados por el notebook, y redacta
la respuesta final citando las cifras reales.

Requisito previo

Ejecutar primero analisis_coffee_high_garden.ipynb (carpeta raiz del proyecto) para que
genere outputs/analysis_summary.json. El chatbot lee ese archivo, no el parquet directo.

Instalacion

    pip install anthropic python-dotenv

Ejecucion sin API key (modo mock)

    python chatbot.py

Si no hay una variable de entorno ANTHROPIC_API_KEY definida, el script entra
automaticamente en modo mock: un menu interactivo con preguntas frecuentes precanned,
respondidas directamente desde los datos, sin llamar a ningun LLM. Sirve para validar
que el script corre sin necesidad de credenciales.

Ejecucion con LLM real (Claude)

Definir la API key como variable de entorno, o crear un archivo .env en esta carpeta con:

    ANTHROPIC_API_KEY=tu_api_key_aqui

y luego correr:

    python chatbot.py

Con la key definida, el chatbot usa el SDK oficial de Anthropic (modelo claude-sonnet-4-5)
con tool-use real para responder preguntas libres en lenguaje natural, por ejemplo:

    Pregunta> cual es el pais con mayor crecimiento de consumo domestico?
    Pregunta> como viene el forecast global para 2024/25?
    Pregunta> en que cluster esta Colombia y que caracteriza a ese grupo?

La API key nunca se pide, guarda ni transmite fuera de este script: el usuario la define
localmente en su propio entorno.

Extensiones futuras propuestas (ver seccion 10 de informe_solucion.md)

- RAG sobre los informes completos (PDF/MD) para responder preguntas mas abiertas.
- Integracion como bot de Slack/Teams para el area de innovacion.
- Generacion automatica de narrativas ejecutivas (resumen semanal/mensual) via LLM.
- Alertas proactivas cuando el forecast o el indice de precios simulado cruce umbrales.
