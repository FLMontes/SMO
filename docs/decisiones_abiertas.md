# Decisiones abiertas — para revisar con Lautaro

Todas están implementadas como parámetros en `config/config.yaml`: cambiar una decisión es cambiar una línea y volver a correr `python ejecutar.py`. La evidencia de cada una está en `docs/resultados_PMV.md`.

| ID | Pregunta | Qué elegí en el PMV y por qué | Qué necesito de vos |
|---|---|---|---|
| D1 | ¿El nodo es la aleación o la aleación + temple? | Aleación + temple, porque Rp0,2 depende del temple. En el caso de rigidez (solo E y ρ), aleación, para evitar duplicados | ¿Ok? ¿Se reporta así? |
| D2 | ¿De dónde salen las tolerancias o vecindades? | ±10 % del rango del atributo en la colección: es la que mejor reproduce a Ashby. Tolerancias por nodo (±% del valor) quedan como alternativa | ¿Hay incertidumbres reales de la fuente? ¿Las buscamos? |
| D3 | ¿Cómo se orienta la red primigenia? | Aleación → elemento ("cita" al elemento), como en las minutas | ¿Era esa la idea de Mancini o Carlos? |
| D4 | ¿Los elementos se rankean? | No: se rankean solo materiales y se renormaliza | — |
| D5 | ¿Qué valor de d? | α = 0,85 (d = 0,15). Influye poco | Corregir la notación en el paper |
| D6 | ¿Datos dudosos (5251‑O, 6063‑O)? | Excluidos (influyen poco) | — |
| D7 | ¿Qué elemento es "aleante"? | El que tiene mínimo en la norma y contenido nominal ≥ 0,1 %. Los "≤x" son impurezas | ¿Coincide con el criterio metalúrgico del equipo? |
| D8 | ¿Las propiedades físicas dependen del temple? | Se suponen independientes | Confirmar |
| D9 | ¿Cómo se ponderan las aristas? | Cada criterio pesa igual al salir de un nodo | ¿Pesos según el exponente del índice de Ashby? |
| D10 | ¿La primigenia participa del ranking? | Sí, pero casi no lo cambia | ¿Qué se espera que aporte? |

## Preguntas generales
1. ¿Qué parte del PMV conviene llevar a la versión final de Argencon y qué parte al póster? Sugerencia: la validación contra Ashby y la figura "red sobre carta de Ashby".
2. ¿Completamos datos mecánicos de más aleaciones (6061, 2024, 5052, 7020)? Es la mejora más barata.
3. ¿Cuál es la fecha límite exacta de la versión final?
4. ¿Cuál es el estado de mi alta formal en el proyecto (SID/SIGEVA)?
