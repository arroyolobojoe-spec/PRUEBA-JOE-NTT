Informe de solución - Reto Tecnico NTT DATA - High Garden Coffee

Autor: Joe Arroyo Fecha: 2026-09-02

Contexto del reto y objetivo de negocio
High Garden Coffee es una exportadora internacional de café. El área de innovación busca aprovechar una base histórica de consumo doméstico de café (1990-2020, 55 paises, distintos tipos de café) para identificar tendencias, información clave y una señal de precios futuros que den ventaja competitiva en el mercado.

El hilo conductor de este informe es que, para una exportadora, el consumo doméstico en los países productores es la otra cara del excedente exportable: a mas consumo doméstico, menos café queda disponible para exportar (todo lo demas constante). Por eso el análisis recorre, en este orden, tendencias globales, crecimiento por país, segmentación de países productores, previsión de consumo, un índice de presión de precios (simulado, con metodología explícita) y detección de eventos anómalos, y cierra con recomendaciones de negocio y una propuesta bonus de chatbot con IA generativa.

Requisitos del reto cubiertos en este documento y en el cuaderno adjunto (analisis_coffee_high_garden.ipynb): análisis de la información (secciones 2 a 4 y 8), solución a problemáticas de negocio con técnicas de analítica (secciones 5, 6 y 7), implementación y evaluación de la solución (metodología y métricas de error en cada sección), presentación de resultados (este documento, con gráficas exportadas en la carpeta charts), y el bonus de IA generativa (sección 10, con demostración funcional en bonus_chatbot/).

Conjunto de datos: descripción y decisiones de preparación
El archivo coffee_db.parquet contiene 55 filas (un país productor por fila) y 33 columnas: Country, Coffee type, 30 columnas de temporada (1990/91 a 2019/20) y Total_domestic_consumption. No tiene valores nulos.

Tipo de café. La columna Tipo de café trae 4 valores: Arábica, Robusta, Arábica/Robusta, Robusta/Arábica. El orden de las etiquetas mixtas no está documentado de forma confiable en la fuente como indicador de variedad predominante, así que para el análisis principal (tendencias, clustering, pronóstico por tipo) se agregan Arábica/Robusta y Robusta/Arábica en una sola categoría Mixto. La columna original se conserva sin modificar por si en el futuro se confirma que el orden si es significativo.

Unidades de consumo. El enunciado del reto dice que el consumo esta en tazas, pero la estructura de la serie (55 paises productores, 1990-2020, valores redondeados a millas) corresponde al formato histórico de consumo doméstico que publica la Organización Internacional del Café (OIC), habitualmente expresado en millas de sacos de 60 kg. No se aplica ninguna conversión sin confirmar la fuente exacta: los ejes y tablas de este informe y del notebook se etiquetan de forma neutral (unidades reportadas por la fuente) para no inducir un error de escalada.

Ausencia de precios. El conjunto de datos no incluye ninguna columna de precios de mercado, aunque el PDF del reto menciona rangos de precios futuros como ejemplo de valor esperado. En vez de solo señalar la limitación, la sección 7 de este informe construye un índice ilustrativo de presión de precios derivados de la dinámica de consumo, dejando explícito en todo momento que es una simulación y no un dato de mercado real.

Formato. Los datos vienen en formato ancho (una columna por temporada). Se transforman a formato largo (País, Tipo de café, Tipo_de_café_agrupado, Temporada, Inicio_año, Consumo) para el análisis de series de tiempo.

Nota de codificación. Algunos nombres de país con tildes o dieresis (por ejemplo Costa de Marfil) pueden verse con caracteres extraños en terminales que no usan UTF-8 (por ejemplo Git Bash en Windows). Se verifico que el dato en si esta correctamente codificado en UTF-8 tanto en el parquet original como en el JSON exportado; es unicamente un problema de visualización en algunos terminales, no un error de los datos.

Análisis exploratorio y tendencias.
El consumo doméstico global crecio de forma sostenida entre 1990/91 y 2019/20: paso de aproximadamente 1.170 millones a 2.999 millones de unidades reportadas por la fuente, un crecimiento acumulado del 156 por ciento en 30 temporadas (grafica charts/01_tendencia_global.png).

Al desagregar por tipo de cafe (charts/02_tendencia_por_tipo.png), el grupo Mixto (paises que producen y consumen tanto Arábica como Robusta) explica la mayor parte del crecimiento en volumen absoluto, dado que incluye a los paises más grandes (Brasil, Indonesia, México, Filipinas, Vietnam, Tailandia).

Los 10 países con mayor consumo doméstico acumulado 1990-2020 (charts/03_top10_paises.png) son, en orden: Brasil, Indonesia, Etiopía, México, Filipinas, Colombia, Venezuela, India, Vietnam y Tailandia. Este grupo concentra la mayor parte del consumo doméstico histórico total y es, por lo tanto, donde una variación en el consumo interno tiene mayor impacto en la oferta exportable global.

Crecimiento y ranking de paises (CAGR)
Regla de cálculo del CAGR (evita divisiones por cero). Se valida que existe al menos un valor positivo en la serie del país. Si 1990/91 es cero, el CAGR se calcula desde el primer año con valor positivo registrado. Si el último año (2019/20) es cero (el país dejo de reportar o perdio todo su consumo doméstico) o si ningún año de la serie es positivo, el CAGR se marca como no disponible y el país se excluye del ranking de crecimiento, pero se documenta aparte como caso especial en la sección 8. Con esta regla, 3 de los 55 paises quedan sin CAGR válido: Zambia, Guinea Ecuatorial y Nepal (detalle en la sección 8).

Top 10 países con mayor crecimiento (CAGR anual 1990/91-2019/20, charts/04_ranking_crecimiento.png):

Tanzania 11,5 por ciento, Vietnam 10,4 por ciento, Tailandia 7,2 por ciento, Costa de Marfil 6,6 por ciento, Nicaragua 6,5 ​​por ciento, Filipinas 5,3 por ciento, Indonesia 4,8 por ciento, Uganda 4,5 por ciento, Etiopía 4,0 por ciento, Brasil 3,5 por ciento.

Top 10 países con mayor declive (CAGR anual, mismo periodo):

Ghana menos 7,1 por ciento, Yemen menos 5,0 por ciento, Togo menos 4,5 por ciento, Gabón menos 4,1 por ciento, Ecuador menos 2,9 por ciento, Malawi menos 2,4 por ciento, Zimbabwe menos 2,4 por ciento, Sri Lanka menos 2,2 por ciento, Sierra Leona menos 2,0 por ciento, Papua Nueva Guinea menos 1,4 por ciento.

Lectura de negocio: Vietnam y Tailandia combinan alto consumo absoluto (están en el top 10 de la sección 3) con alto crecimiento, es decir, están absorbiendo cada vez más de su propia producción. Brasil, aunque es el mayor consumidor absoluto, crece a un ritmo moderado (3,5 por ciento anual), mientras que países como Ghana, Togo y Gabón muestran declive sostenido en su consumo interno, lo que en principio deja más excedente exportable disponible con el tiempo si su producción se mantiene.

Segmentación de países productores (clustering)
Se agruparon los 55 países según tres características de su patrón de consumo doméstico: nivel promedio (en escala logarítmica), crecimiento (CAGR) y volatilidad (desviación estándar de las variaciones interanuales). Los 3 países sin CAGR válido (Zambia, Guinea Ecuatorial, Nepal) se excluyeron del clustering por no tener una señal de crecimiento comparable.

Se probaron particiones de 2 a 6 grupos con KMeans (random_state=42) y se elige el número de grupos con mejor Silhouette Score, resultando en 3 segmentos (charts/05_clusters_pca.png, proyectados en 2 dimensiones con PCA, también con random_state=42 para reproducibilidad):

Clúster 0, 3 países (Costa de Marfil, Nicaragua, Tanzania): crecimiento promedio muy alto (8,2 por ciento anual) pero con volatilidad muy alta (80,9 por ciento). Son mercados pequeños y erráticos que crecen rápidamente: vale la pena monitorearlos de cerca porque su comportamiento es difícil de proyectar con precisión.

El cluster 1, 30 países, incluye a casi todos los grandes consumidores (Brasil, Indonesia, Etiopía, México, Colombia, Venezuela, India, Vietnam, Filipinas, Tailandia, entre otros): crecimiento moderado (2,0 por ciento anual) y volatilidad relativamente baja (7,9 por ciento). Es el segmento más estable y el que más peso tiene en el volumen total: la mayor parte de la planificacion comercial de mediano plazo deberia apoyarse en el comportamiento de este grupo.

Clúster 2, 19 países (Angola, Burundi, República Centroafricana, Congo, Gabón, Ghana, Guyana, Jamaica, Liberia, Malawi, Papua Nueva Guinea, Ruanda, Sierra Leona, Sri Lanka, Timor-Leste, Togo, Trinidad y Tobago, Yemen, Zimbabwe): crecimiento promedio negativo (menos 1,3 por ciento anual) y volatilidad intermedia (21,7 por ciento). Son mercados en declive de consumo doméstico, en general productores más pequeños: representan una oportunidad relativa de mayor excedente exportable en el tiempo, aunque con más incertidumbre por su volatilidad.

Previsión de consumo doméstico
Con solo 30 puntos anuales por país, ajustar 55 modelos individuales finos arriesga sobreajuste. Se compara, mediante backtesting sobre la serie global (entrenando hasta 2014/15 y evaluando 2015/16-2019/20), un modelo de tendencia lineal contra un modelo Holt (suavizado exponencial con tendencia amortiguada, sin componente estacional por tratarse de datos anuales). El método con menor error porcentual absoluto medio (MAPE) en el backtest fue Holt, con un MAPE de 1.48 por ciento (la tendencia lineal tuvo un error mayor en el mismo backtest). Ese método, elegido una sola vez mediante el backtest global, se aplica después para proyectar 5 años (2020/21 a 2024/25) sobre el agregado global, cada tipo de café agregado y los 10 países de mayor consumo. No se proyectaron los 55 paises individualmente para no dar una falsa sensación de precisión con series tan cortas.

Resultado del pronóstico global (charts/06_forecast_global.png), con banda de incertidumbre aproximada del 80 por ciento calculado a partir del error residual del backtest:

2020/21 aproximadamente 3.008 millones (rango 2.953 a 3.063 millones) 2021/22 aproximadamente 3.017 millones (rango 2.962 a 3.072 millones) 2022/23 aproximadamente 3.026 millones (rango 2.971 a 3.080 millones) 2023/24 aproximadamente 3.034 millones (rango 2.979 a 3.089 millones) 2024/25 aproximadamente 3.042 millones (rango 2.987 a 3.096 millones)

El resultado completo por tipo de café y por cada uno de los 10 países de mayor consumo queda disponible en el notebook (sección 5) y en outputs/analysis_summary.json.

Índice de presión de precios (simulado)
El conjunto de datos no incluye precios de mercado. Para responder al pedido explícito del reto de rangos de precios futuros sin inventar datos de mercado como si fueran reales, se construyó un índice ilustrativo con metodología transparente, diseñado como un oscilador de presión (no como un nivel de precio compuesto, que se dispararia matemáticamente si se capitaliza un crecimiento sostenido durante 30 años):

Indice en el anio t = 100 + k por 100 por (crecimiento del consumo global en t menos el crecimiento promedio historico) mas un termino de ruido aleatorio pequeno.

Intuición: si el consumo doméstico global crece un año por encima de su promedio histórico, una porción mayor de la producción se queda en el país de origen ese año, ajustando el excedente exportable disponible por debajo de lo habitual, lo que se traduce en el índice como una señal de mayor presión al alza sobre precios (valor por encima de 100). Si crece por debajo de su promedio histórico, la señal es de menor presión (valor por debajo de 100). La constante k (usada como 3.0) es una sensibilidad ilustrativa, no calibrada con datos de mercado reales, y el ruido aleatorio (semilla fija, random_state=42) representa la variabilidad real de precios que este único indicador no puede explicar.

Aviso explícito: este índice no son precios reales de café, es una simulación con multas demostrativas, acotada alrededor de 100 para que su escala se lea como una señal de tensión relativa y no como un nivel de precio en dólares. Para una versión productiva se requerirá integrar datos reales, por ejemplo el indicador compuesto de la OIC o los futuros de cafe de ICE (charts/07_indice_precio_simulado.png).

Con esta metodología, el índice cierra 2019/20 en 88.9 (por debajo de neutral, reflejando que el crecimiento de consumo de los últimos años de la serie estuvo por debajo del promedio histórico) y la proyección simulada para 2020/21-2024/25 oscila entre aproximadamente 90.0 y 93.1, siempre alrededor del nivel neutral.

Anomalías y eventos relevantes
Se calcula la variacion interanual (YoY) de consumo por pais y su z-score dentro de la propia serie de cada pais (para no comparar volatilidades de paises con escalas muy distintas entre si). Se marcaron como anomalías los puntos con z-score absoluto mayor a 2.5. El detalle completo de los 15 casos mas extremos esta en el cuaderno (sección 7).

Además de pico esoss puntuales, hay 3 casos estructurales que son información clave para negocio y que no siempre aparecen como un pico aislado:

Zambia: el consumo doméstico reportado cae a cero de forma sostenida desde 2009/10 hasta 2019/20 (11 temporadas seguidas en cero), tras venir de un rango de 36.000 a 90.000 unidades en las temporadas anteriores. Es una interrupción de informe o de actividad, no una fluctuación normal. Se recomienda verificar con la fuente antes de usar este país en decisiones comerciales.

Guinea Ecuatorial y Nepal: no tienen ningún valor positivo registrado en las 30 temporadas. Es probable que sean países sin consumo doméstico material o sin cobertura de reporte de la fuente. Por eso se excluyeron de los rankings de crecimiento (sección 4) y del clustering (sección 5).

Conclusiones y recomendaciones de negocio.
Consumo global: el consumo doméstico global crecio de forma sostenida entre 1990/91 y 2019/20 (156 por ciento acumulado), lo que estructuralmente reduce el excedente exportable disponible en el tiempo si la producción no crece al mismo ritmo.

Concentracion: un grupo reducido de paises (Brasil, Indonesia, Etiopia, Mexico, Filipinas, Colombia, Venezuela, India, Vietnam, Tailandia) concentra la mayor parte del consumo domestico historico acumulado. Son los mercados donde una variación en su consumo interno tiene mayor impacto en la oferta exportable global, y donde vale la pena priorizar el monitoreo continuo.

Segmentacion accionable: los paises del cluster de mayor crecimiento (sección 5, cluster 0) son una señal de alerta temprana para asegurar contratos de suministro a largo plazo antes de que su excedente exportable se reduzca mas. Los países del cluster en declive (cluster 2) liberan, en principio, más excedente exportable en el tiempo, y son candidatos a fortalecer relaciones comerciales de abastecimiento, aunque con más incertidumbre por su volatilidad. El cluster estable (cluster 1) concentra el grueso del volumen y deberia ser la base de la planificacion comercial de mediano plazo.

Forecast: la proyección a 2024/25 (sección 6) da una primera estimación cuantitativa para planear volúmenes de compra y exportación a mediano plazo, con una banda de incertidumbre explícita en vez de un número único, y con un error de backtest bajo (MAPE 1.48 por ciento en la serie global).

Precios: el índice de presión de precios (sección 7) es una prueba de concepto que conecta la dinámica de consumo con una señal de precio. Para uso real en decisiones comerciales debe sustituirse o calibrarse con datos de mercado reales (por ejemplo el indicador compuesto de la OIC o los futuros de cafe de ICE), no usar tal cual.

Calidad de datos: se recomienda a los equipos de producto y datos verificar los 3 casos señalados en la sección 8 (Zambia, Guinea Ecuatorial, Nepal) con la fuente original antes de tomarlos como insumo de decisiones comerciales.

Bono: chatbot con IA generativa
Se desarrolló una demo funcional en bonus_chatbot/chatbot.py: un chatbot de línea de comandos que responde preguntas en lenguaje natural sobre este análisis (tendencias, ranking de crecimiento, clusters, pronóstico, índice de precios simulado).

Arquitectura. El notebook exporta un resumen estructurado de todos los resultados a outputs/analysis_summary.json (totales por país, CAGR, cluster asignado, pronósticos, índice de precios). El chatbot define un conjunto acotado de funciones de consulta sobre ese resumen (por ejemplo obtener estadísticas de un país, obtener el ranking de crecimiento, obtener el perfil de un cluster, obtener un pronóstico, obtener el índice de precios) y las exponen al modelo Claude como herramientas mediante el patrón de uso de herramientas del SDK oficial de Anthropic: el modelo decide que función invocar según la pregunta del usuario, recibe el resultado real de los datos, y redacta la respuesta final en lenguaje natural citando esas cifras. Deliberadamente no se le da al modelo la capacidad de ejecutar código arbitrario sobre los datos, para mantener las respuestas acotadas y verificables.

Modo sin clave API. Si no hay una variable de entorno ANTHROPIC_API_KEY configurada (ni un archivo .env local), el script cae automáticamente a un modo simulado con un menú interactivo de preguntas frecuentes precanned, respondidas directamente desde los datos sin llamar a ningún LLM. Esto permite que cualquier persona que revise el reto pueda ejecutar el chatbot de inmediato sin necesidad de configurar credenciales externas. Instrucciones completas de instalación y ejecución en bonus_chatbot/README.md.

Extensiones futuras propuestas para dar más valor con IA generativa:

RAG sobre los informes completos (este documento y el PDF del reto original) para responder preguntas más abiertas y con más contexto narrativo, no solo sobre cifras estructuradas.

Integracion como bot de Slack o Teams para que el área de innovación consulte el estado de los mercados sin salir de su flujo de trabajo diario.

Generacion automatica de narrativas ejecutivas (un resumen semanal o mensual redactado por el LLM a partir de los datos mas recientes) para reducir el trabajo manual de reporteria.

Alertas proactivas: que el mismo pipeline que genera el pronóstico y el índice de precios dispare una alerta (vía el chatbot o por correo) cuando el pronóstico de algún país clave o el índice de presión de precios simulado cruza un umbral definido por el negocio.

Si en el futuro se integra una fuente real de precios de mercado, el mismo patrón de uso de herramientas del chatbot se puede extender con una función adicional que consulta esa fuente, sin cambiar la arquitectura general.

Archivos entregados

analisis_coffee_high_garden.ipynb, cuaderno completo y ejecutado con todo el análisis. informe_solucion.md, este documento. charts/, gráficas exportadas en PNG referenciadas en este informe. outputs/analysis_summary.json, resumen de datos estructurados usados ​​por el chatbot. bonus_chatbot/chatbot.py y bonus_chatbot/README.md, demostración funcional del bono de IA generativa.

