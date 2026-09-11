Informe de solucion - Reto Tecnico NTT DATA - High Garden Coffee

Autor: Joe Arroyo
Fecha: 2026-09-02

1. Contexto del reto y objetivo de negocio

High Garden Coffee es una exportadora internacional de cafe. El area de innovacion busca
aprovechar una base historica de consumo domestico de cafe (1990-2020, 55 paises, distintos
tipos de cafe) para identificar tendencias, informacion clave y una senal de precios futuros
que den ventaja competitiva en el mercado.

El hilo conductor de este informe es que, para una exportadora, el consumo domestico en los
paises productores es la otra cara del excedente exportable: a mas consumo domestico, menos
cafe queda disponible para exportar (todo lo demas constante). Por eso el analisis recorre,
en este orden, tendencias globales, crecimiento por pais, segmentacion de paises
productores, forecasting de consumo, un indice de presion de precios (simulado, con
metodologia explicita) y deteccion de eventos anomalos, y cierra con recomendaciones de
negocio y una propuesta bonus de chatbot con IA generativa.

Requisitos del reto cubiertos en este documento y en el notebook adjunto
(analisis_coffee_high_garden.ipynb): analisis de la informacion (secciones 2 a 4 y 8),
solucion a problematicas de negocio con tecnicas de analitica (secciones 5, 6 y 7),
implementacion y evaluacion de la solucion (metodologia y metricas de error en cada
seccion), presentacion de resultados (este documento, con graficas exportadas en la
carpeta charts), y el bonus de IA generativa (seccion 10, con demo funcional en
bonus_chatbot/).

2. Dataset: descripcion y decisiones de preparacion

El archivo coffee_db.parquet contiene 55 filas (un pais productor por fila) y 33 columnas:
Country, Coffee type, 30 columnas de temporada (1990/91 a 2019/20) y
Total_domestic_consumption. No tiene valores nulos.

Tipo de cafe. La columna Coffee type trae 4 valores: Arabica, Robusta, Arabica/Robusta,
Robusta/Arabica. El orden de las etiquetas mixtas no esta documentado de forma confiable en
la fuente como indicador de variedad predominante, asi que para el analisis principal
(tendencias, clustering, forecasting por tipo) se agregan Arabica/Robusta y Robusta/Arabica
en una sola categoria Mixto. La columna original se conserva sin modificar por si en el
futuro se confirma que el orden si es significativo.

Unidades de consumo. El enunciado del reto dice que el consumo esta en tazas, pero la
estructura de la serie (55 paises productores, 1990-2020, valores redondeados a miles)
corresponde al formato historico de consumo domestico que publica la Organizacion
Internacional del Cafe (OIC), habitualmente expresado en miles de sacos de 60 kg. No se
aplica ninguna conversion sin confirmar la fuente exacta: los ejes y tablas de este informe
y del notebook se etiquetan de forma neutral (unidades reportadas por la fuente) para no
inducir un error de escala.

Ausencia de precios. El dataset no incluye ninguna columna de precios de mercado, aunque el
PDF del reto menciona rangos de precios futuros como ejemplo de valor esperado. En vez de
solo senalar la limitacion, la seccion 7 de este informe construye un indice ilustrativo de
presion de precios derivado de la dinamica de consumo, dejando explicito en todo momento que
es una simulacion y no un dato de mercado real.

Formato. Los datos vienen en formato ancho (una columna por temporada). Se transforman a
formato largo (Country, Coffee type, Coffee_type_grouped, Season, Year_start, Consumption)
para el analisis de series de tiempo.

Nota de codificacion. Algunos nombres de pais con tildes o dieresis (por ejemplo Cote
d'Ivoire) pueden verse con caracteres extranos en terminales que no usan UTF-8 (por ejemplo
Git Bash en Windows). Se verifico que el dato en si esta correctamente codificado en UTF-8
tanto en el parquet original como en el JSON exportado; es unicamente un problema de
visualizacion en algunas terminales, no un error de los datos.

3. Analisis exploratorio y tendencias

El consumo domestico global crecio de forma sostenida entre 1990/91 y 2019/20: paso de
aproximadamente 1.170 millones a 2.999 millones de unidades reportadas por la fuente, un
crecimiento acumulado del 156 por ciento en 30 temporadas (grafica
charts/01_tendencia_global.png).

Al desagregar por tipo de cafe (charts/02_tendencia_por_tipo.png), el grupo Mixto (paises
que producen y consumen tanto Arabica como Robusta) explica la mayor parte del crecimiento
en volumen absoluto, dado que incluye a los paises mas grandes (Brasil, Indonesia, Mexico,
Filipinas, Vietnam, Tailandia).

Los 10 paises con mayor consumo domestico acumulado 1990-2020
(charts/03_top10_paises.png) son, en orden: Brasil, Indonesia, Etiopia, Mexico, Filipinas,
Colombia, Venezuela, India, Vietnam y Tailandia. Este grupo concentra la mayor parte del
consumo domestico historico total y es, por lo tanto, donde una variacion en el consumo
interno tiene mayor impacto en la oferta exportable global.

4. Crecimiento y ranking de paises (CAGR)

Regla de calculo del CAGR (evita divisiones por cero). Se valida que exista al menos un
valor positivo en la serie del pais. Si 1990/91 es cero, el CAGR se calcula desde el primer
anio con valor positivo registrado. Si el ultimo anio (2019/20) es cero (el pais dejo de
reportar o perdio todo su consumo domestico) o si ningun anio de la serie es positivo, el
CAGR se marca como no disponible y el pais se excluye del ranking de crecimiento, pero se
documenta aparte como caso especial en la seccion 8. Con esta regla, 3 de los 55 paises
quedan sin CAGR valido: Zambia, Equatorial Guinea y Nepal (detalle en la seccion 8).

Top 10 paises con mayor crecimiento (CAGR anual 1990/91-2019/20,
charts/04_ranking_crecimiento.png):

Tanzania 11.5 por ciento, Vietnam 10.4 por ciento, Tailandia 7.2 por ciento, Costa de Marfil
6.6 por ciento, Nicaragua 6.5 por ciento, Filipinas 5.3 por ciento, Indonesia 4.8 por ciento,
Uganda 4.5 por ciento, Etiopia 4.0 por ciento, Brasil 3.5 por ciento.

Top 10 paises con mayor declive (CAGR anual, mismo periodo):

Ghana menos 7.1 por ciento, Yemen menos 5.0 por ciento, Togo menos 4.5 por ciento, Gabon
menos 4.1 por ciento, Ecuador menos 2.9 por ciento, Malawi menos 2.4 por ciento, Zimbabwe
menos 2.4 por ciento, Sri Lanka menos 2.2 por ciento, Sierra Leone menos 2.0 por ciento,
Papua Nueva Guinea menos 1.4 por ciento.

Lectura de negocio: Vietnam y Tailandia combinan alto consumo absoluto (estan en el top 10
de la seccion 3) con alto crecimiento, es decir, estan absorbiendo cada vez mas de su propia
produccion. Brasil, aunque es el mayor consumidor absoluto, crece a un ritmo moderado (3.5
por ciento anual), mientras que paises como Ghana, Togo y Gabon muestran declive sostenido
en su consumo interno, lo que en principio deja mas excedente exportable disponible con el
tiempo si su produccion se mantiene.

5. Segmentacion de paises productores (clustering)

Se agruparon los 55 paises segun tres caracteristicas de su patron de consumo domestico:
nivel promedio (en escala logaritmica), crecimiento (CAGR) y volatilidad (desviacion
estandar de las variaciones interanuales). Los 3 paises sin CAGR valido (Zambia, Equatorial
Guinea, Nepal) se excluyeron del clustering por no tener una senal de crecimiento
comparable.

Se probaron particiones de 2 a 6 grupos con KMeans (random_state=42) y se eligio el numero
de grupos con mejor silhouette score, resultando en 3 segmentos
(charts/05_clusters_pca.png, proyectados en 2 dimensiones con PCA, tambien con
random_state=42 para reproducibilidad):

Cluster 0, 3 paises (Costa de Marfil, Nicaragua, Tanzania): crecimiento promedio muy alto
(8.2 por ciento anual) pero con volatilidad muy alta (80.9 por ciento). Son mercados
pequenos y erraticos que crecen rapido: vale la pena monitorearlos de cerca porque su
comportamiento es dificil de proyectar con precision.

Cluster 1, 30 paises, incluye a casi todos los grandes consumidores (Brasil, Indonesia,
Etiopia, Mexico, Colombia, Venezuela, India, Vietnam, Filipinas, Tailandia, entre otros):
crecimiento moderado (2.0 por ciento anual) y volatilidad relativamente baja (7.9 por
ciento). Es el segmento mas estable y el que mas peso tiene en el volumen total: la mayor
parte de la planificacion comercial de mediano plazo deberia apoyarse en el comportamiento
de este grupo.

Cluster 2, 19 paises (Angola, Burundi, Republica Centroafricana, Congo, Gabon, Ghana,
Guyana, Jamaica, Liberia, Malawi, Papua Nueva Guinea, Ruanda, Sierra Leona, Sri Lanka,
Timor-Leste, Togo, Trinidad y Tobago, Yemen, Zimbabwe): crecimiento promedio negativo
(menos 1.3 por ciento anual) y volatilidad intermedia (21.7 por ciento). Son mercados en
declive de consumo domestico, en general productores mas pequenos: representan una
oportunidad relativa de mayor excedente exportable en el tiempo, aunque con mas
incertidumbre por su volatilidad.

6. Forecasting de consumo domestico

Con solo 30 puntos anuales por pais, ajustar 55 modelos individuales finos arriesga
sobreajuste. Se comparo, mediante backtesting sobre la serie global (entrenando hasta
2014/15 y evaluando 2015/16-2019/20), un modelo de tendencia lineal contra un modelo Holt
(suavizado exponencial con tendencia amortiguada, sin componente estacional por tratarse de
datos anuales). El metodo con menor error porcentual absoluto medio (MAPE) en el backtest
fue Holt, con un MAPE de 1.48 por ciento (la tendencia lineal tuvo un error mayor en el
mismo backtest). Ese metodo, elegido una sola vez mediante el backtest global, se aplico
despues para proyectar 5 anios (2020/21 a 2024/25) sobre el agregado global, cada tipo de
cafe agregado y los 10 paises de mayor consumo. No se proyectaron los 55 paises
individualmente para no dar una falsa sensacion de precision con series tan cortas.

Resultado del forecast global (charts/06_forecast_global.png), con banda de incertidumbre
aproximada del 80 por ciento calculada a partir del error residual del backtest:

2020/21 aproximadamente 3.008 millones (rango 2.953 a 3.063 millones)
2021/22 aproximadamente 3.017 millones (rango 2.962 a 3.072 millones)
2022/23 aproximadamente 3.026 millones (rango 2.971 a 3.080 millones)
2023/24 aproximadamente 3.034 millones (rango 2.979 a 3.089 millones)
2024/25 aproximadamente 3.042 millones (rango 2.987 a 3.096 millones)

El resultado completo por tipo de cafe y por cada uno de los 10 paises de mayor consumo
queda disponible en el notebook (seccion 5) y en outputs/analysis_summary.json.

7. Indice de presion de precios (simulado)

El dataset no incluye precios de mercado. Para responder al pedido explicito del reto de
rangos de precios futuros sin inventar datos de mercado como si fueran reales, se construyo
un indice ilustrativo con metodologia transparente, disenado como un oscilador de presion
(no como un nivel de precio compuesto, que se dispararia matematicamente si se capitaliza un
crecimiento sostenido durante 30 anios):

Indice en el anio t = 100 + k por 100 por (crecimiento del consumo global en t menos el
crecimiento promedio historico) mas un termino de ruido aleatorio pequeno.

Intuicion: si el consumo domestico global crece un anio por encima de su promedio
historico, una porcion mayor de la produccion se queda en el pais de origen ese anio,
ajustando el excedente exportable disponible por debajo de lo habitual, lo que se traduce en
el indice como una senal de mayor presion al alza sobre precios (valor por encima de 100).
Si crece por debajo de su promedio historico, la senal es de menor presion (valor por debajo
de 100). La constante k (usada como 3.0) es una sensibilidad ilustrativa, no calibrada con
datos de mercado reales, y el ruido aleatorio (semilla fija, random_state=42) representa la
variabilidad real de precios que este unico indicador no puede explicar.

Aviso explicito: este indice no son precios reales de cafe, es una simulacion con fines
demostrativos, acotada alrededor de 100 para que su escala se lea como una senal de tension
relativa y no como un nivel de precio en dolares. Para una version productiva se requeriria
integrar datos reales, por ejemplo el indicador compuesto de la OIC o los futuros de cafe de
ICE (charts/07_indice_precio_simulado.png).

Con esta metodologia, el indice cierra 2019/20 en 88.9 (por debajo de neutral, reflejando
que el crecimiento de consumo de los ultimos anios de la serie estuvo por debajo del
promedio historico) y la proyeccion simulada para 2020/21-2024/25 oscila entre
aproximadamente 90.0 y 93.1, siempre alrededor del nivel neutral.

8. Anomalias y eventos relevantes

Se calculo la variacion interanual (YoY) de consumo por pais y su z-score dentro de la
propia serie de cada pais (para no comparar volatilidades de paises con escalas muy
distintas entre si). Se marcaron como anomalias los puntos con z-score absoluto mayor a 2.5.
El detalle completo de los 15 casos mas extremos esta en el notebook (seccion 7).

Ademas de esos picos puntuales, hay 3 casos estructurales que son informacion clave para
negocio y que no siempre aparecen como un pico aislado:

Zambia: el consumo domestico reportado cae a cero de forma sostenida desde 2009/10 hasta
2019/20 (11 temporadas seguidas en cero), tras venir de un rango de 36.000 a 90.000 unidades
en las temporadas anteriores. Es una interrupcion de reporte o de actividad, no una
fluctuacion normal. Se recomienda verificar con la fuente antes de usar este pais en
decisiones comerciales.

Equatorial Guinea y Nepal: no tienen ningun valor positivo registrado en las 30 temporadas.
Es probable que sean paises sin consumo domestico material o sin cobertura de reporte de la
fuente. Por eso se excluyeron de los rankings de crecimiento (seccion 4) y del clustering
(seccion 5).

9. Conclusiones y recomendaciones de negocio

Consumo global: el consumo domestico global crecio de forma sostenida entre 1990/91 y
2019/20 (156 por ciento acumulado), lo que estructuralmente reduce el excedente exportable
disponible en el tiempo si la produccion no crece al mismo ritmo.

Concentracion: un grupo reducido de paises (Brasil, Indonesia, Etiopia, Mexico, Filipinas,
Colombia, Venezuela, India, Vietnam, Tailandia) concentra la mayor parte del consumo
domestico historico acumulado. Son los mercados donde una variacion en su consumo interno
tiene mayor impacto en la oferta exportable global, y donde vale la pena priorizar el
monitoreo continuo.

Segmentacion accionable: los paises del cluster de mayor crecimiento (seccion 5, cluster 0)
son una senal de alerta temprana para asegurar contratos de suministro a largo plazo antes
de que su excedente exportable se reduzca mas. Los paises del cluster en declive (cluster 2)
liberan, en principio, mas excedente exportable en el tiempo, y son candidatos a fortalecer
relaciones comerciales de abastecimiento, aunque con mas incertidumbre por su volatilidad.
El cluster estable (cluster 1) concentra el grueso del volumen y deberia ser la base de la
planificacion comercial de mediano plazo.

Forecast: la proyeccion a 2024/25 (seccion 6) da una primera estimacion cuantitativa para
planear volumenes de compra y exportacion a mediano plazo, con una banda de incertidumbre
explicita en vez de un numero unico, y con un error de backtest bajo (MAPE 1.48 por ciento
en la serie global).

Precios: el indice de presion de precios (seccion 7) es una prueba de concepto que conecta
la dinamica de consumo con una senal de precio. Para uso real en decisiones comerciales debe
sustituirse o calibrarse con datos de mercado reales (por ejemplo el indicador compuesto de
la OIC o los futuros de cafe de ICE), no usarse tal cual.

Calidad de datos: se recomienda a los equipos de producto y datos verificar los 3 casos
senalados en la seccion 8 (Zambia, Equatorial Guinea, Nepal) con la fuente original antes de
tomarlos como insumo de decisiones comerciales.

10. Bonus: chatbot con IA generativa

Se desarrollo una demo funcional en bonus_chatbot/chatbot.py: un chatbot de linea de
comandos que responde preguntas en lenguaje natural sobre este analisis (tendencias, ranking
de crecimiento, clusters, forecast, indice de precios simulado).

Arquitectura. El notebook exporta un resumen estructurado de todos los resultados a
outputs/analysis_summary.json (totales por pais, CAGR, cluster asignado, forecasts, indice
de precios). El chatbot define un conjunto acotado de funciones de consulta sobre ese
resumen (por ejemplo obtener estadisticas de un pais, obtener el ranking de crecimiento,
obtener el perfil de un cluster, obtener un forecast, obtener el indice de precios) y las
expone al modelo Claude como tools mediante el patron de tool-use del SDK oficial de
Anthropic: el modelo decide que funcion invocar segun la pregunta del usuario, recibe el
resultado real de los datos, y redacta la respuesta final en lenguaje natural citando esas
cifras. Deliberadamente no se le da al modelo la capacidad de ejecutar codigo arbitrario
sobre los datos, para mantener las respuestas acotadas y verificables.

Modo sin API key. Si no hay una variable de entorno ANTHROPIC_API_KEY configurada (ni un
archivo .env local), el script cae automaticamente a un modo mock con un menu interactivo de
preguntas frecuentes precanned, respondidas directamente desde los datos sin llamar a ningun
LLM. Esto permite que cualquier persona que revise el reto pueda ejecutar el chatbot de
inmediato sin necesidad de configurar credenciales externas. Instrucciones completas de
instalacion y ejecucion en bonus_chatbot/README.md.

Extensiones futuras propuestas para dar mas valor con IA generativa:

RAG sobre los informes completos (este documento y el PDF del reto original) para responder
preguntas mas abiertas y con mas contexto narrativo, no solo sobre cifras estructuradas.

Integracion como bot de Slack o Teams para que el area de innovacion consulte el estado de
los mercados sin salir de su flujo de trabajo diario.

Generacion automatica de narrativas ejecutivas (un resumen semanal o mensual redactado por
el LLM a partir de los datos mas recientes) para reducir el trabajo manual de reporteria.

Alertas proactivas: que el mismo pipeline que genera el forecast y el indice de precios
dispare una alerta (via el chatbot o por correo) cuando el forecast de algun pais clave o el
indice de presion de precios simulado cruce un umbral definido por el negocio.

Si en el futuro se integra una fuente real de precios de mercado, el mismo patron de
tool-use del chatbot se puede extender con una funcion adicional que consulte esa fuente,
sin cambiar la arquitectura general.

Archivos entregados

analisis_coffee_high_garden.ipynb, notebook completo y ejecutado con todo el analisis.
informe_solucion.md, este documento.
charts/, graficas exportadas en PNG referenciadas en este informe.
outputs/analysis_summary.json, resumen de datos estructurado usado por el chatbot.
bonus_chatbot/chatbot.py y bonus_chatbot/README.md, demo funcional del bonus de IA
generativa.
