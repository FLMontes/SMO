# Resultados del PMV — "armado prototipo" con aleaciones de Al

Corrida del 01/10/2026 con `config/config.yaml` por defecto. Se regenera con `python ejecutar.py`; los archivos quedan en `outputs/`.

## Qué se construyó

| Elemento | Valor |
|---|---|
| Nodos-material (aleación + temple) | 45, de 9 aleaciones (1050, 2011, 3103, 5083, 5251, 5754, 6063, 6082, 7075) |
| Nodos-material (solo aleación, caso de rigidez) | 33 |
| Atributos | E, Rp0,2, ρ, α, T sólidus |
| Red primaria (aleación + temple) | 2665 aristas orientadas, una por cada atributo que se sobrelapa |
| Red primigenia | 148 aristas material → elemento, hacia 9 elementos aleantes |
| Vecindad | ±10 % del rango de cada atributo en la colección |
| PageRank | α = 0,85 (d = 0,15), ponderación por atributo |

Por qué quedan solo 45 nodos: de las 34 aleaciones de la BD, solo 10 tienen propiedades mecánicas. Una de ellas (6262) no tiene físicas y se descarta. También se excluyen los dos datos dudosos (5251‑O y 6063‑O).

## Validación contra Ashby

| Caso de diseño | Índice de Ashby | Spearman ρs | Top‑5 en común | 1º PageRank | 1º Ashby |
|---|---|---|---|---|---|
| Tirante liviano y resistente | σy/ρ | **0,71** | **5 de 5** | 5083‑HX9 | 7075‑T6 |
| Viga liviana y resistente | σy^(2/3)/ρ | **0,72** | **5 de 5** | 5083‑HX9 | 7075‑T6 |
| Viga liviana y rígida (bicicleta) | E^(1/2)/ρ | **0,61** | 3 de 5 | 5083 | 5083 |

**Lectura.** El método reproduce en buena medida el ranking de Ashby. En los dos casos de resistencia, los 5 mejores candidatos son los mismos (5083 endurecida y 7075), aunque en otro orden.

La diferencia principal es que PageRank premia a los materiales **bien conectados con vecinos buenos**: la familia 5083, con muchos temples cercanos entre sí. El índice de Ashby, en cambio, premia el valor extremo aislado: 7075‑T6, que no tiene vecinos en Rp0,2. Es el comportamiento esperable de PageRank ("un nodo es relevante si está conectado con nodos relevantes") y es un resultado para discutir en el paper.

## Sensibilidad (`outputs/sensibilidad.csv` y `sensibilidad.png`)

Spearman ρs según el ancho de vecindad (con red primigenia):

| Vecindad (fracción del rango) | 0,025 | 0,05 | 0,10 | 0,15 | 0,20 | 0,30 |
|---|---|---|---|---|---|---|
| Tirante (σy/ρ) | −0,10 | 0,38 | 0,71 | 0,76 | 0,76 | 0,83 |
| Viga rígida (√E/ρ) | 0,29 | 0,82 | 0,61 | 0,38 | 0,17 | 0,33 |

Efecto de cada decisión abierta (ρs: tirante / viga resistente / viga rígida):

| Variante | ρs | Top‑5 en común |
|---|---|---|
| **PMV (por defecto)** | **0,71 / 0,72 / 0,61** | 5 / 5 / 3 |
| Tolerancia porcentual (±% del valor) | 0,50 / 0,50 / 0,00 | 3 / 3 / 2 |
| Ponderación uniforme | 0,56 / 0,56 / 0,88 | 3 / 3 / 4 |
| Sin primigenia en la selección | 0,71 / 0,71 / 0,64 | 4 / 4 / 4 |
| Primigenia bidireccional | 0,70 / 0,70 / 0,34 | 4 / 4 / 3 |
| Incluir datos dudosos | 0,71 / 0,71 / 0,61 | 5 / 5 / 3 |
| α = 0,5 | 0,71 / 0,72 / 0,62 | 4 / 4 / 3 |

## Hallazgos para el paper

1. **El ancho de vecindad es el parámetro que más pesa**, más que d. Vecindades chicas fragmentan la red y PageRank no puede propagar. Vecindades grandes la vuelven casi completa y el ranking pierde información.
2. **Las vecindades deben normalizarse por atributo.** Con ±% del valor, atributos que varían poco (ρ, E, ~6 %) generan redes muy densas que "arrastran" a los caminantes, y el acuerdo con Ashby cae (0,50 / 0,00). Normalizar por el rango de la colección resuelve el problema de las unidades distintas (minuta del 14/04/2026).
3. **Los nodos con atributos idénticos forman cliques** (aristas en ambos sentidos) que retienen caminantes. Cuando los criterios son solo propiedades físicas, que no dependen del temple, el nodo debe ser la aleación y no la aleación + temple.
4. **La red primigenia hacia los elementos casi no cambia el ranking** (los elementos son sumideros y redistribuyen uniformemente). En modo bidireccional lo empeora en el caso de rigidez. Su valor parece estar más en explorar relaciones de composición que en el ranking.
5. **No hay una configuración óptima para todos los casos** (p. ej. la ponderación uniforme favorece el caso de rigidez y perjudica los de resistencia). Conviene reportarlo así: el método tiene hiperparámetros como cualquier heurística.
6. **Notación de d.** En la fórmula del paper, d es la fracción de teletransporte. El "d = 0,85" que se menciona corresponde en networkx a α = 0,85, es decir d = 0,15.

## Limitaciones

- Solo 9 aleaciones con datos mecánicos completos. Completar 6061, 2024, 5052, 7020 y otras mejoraría mucho la red.
- Las tolerancias no salen de la fuente: son supuestas.
- El precio queda fuera por falta de datos.
- La validación toma a Ashby como referencia: un acuerdo perfecto no es el objetivo, pero un desacuerdo grande sería una señal de alarma.
