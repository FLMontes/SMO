# CLAUDE.md — Proyecto SMO

Instrucciones para Claude Code en este repositorio.

## Quién y cómo
- Trabajo con Franco, estudiante de Ingeniería en Computación. Llamalo Franco y empezá cada respuesta con "Franco:".
- Respuestas en español, claras y concisas. Está aprendiendo a trabajar con Claude Code: explicá brevemente qué vas a hacer y por qué antes de cambios no triviales.
- Franco responde a Lautaro, responsable del proyecto en el laboratorio.

## Qué es el proyecto
SMO (internamente "Gemas"; PIDTA SeCyT‑UNC 2026, Depto. de Materiales y Tecnología, FCEFyN‑UNC): selección de materiales con la lógica de Ashby, donde la colección de materiales es una red y PageRank rankea a los candidatos. Hay un trabajo aceptado en Argencon 2026 (IEEE, 11–13/11/2026): la versión final se entrega en octubre y además hay que hacer un póster.

Flujo del laboratorio: Datos crudos → Datos curados → Objetos (pandas) → Base de datos (SQLite) → Red (networkx).

**Contexto completo:** `referencias/README.md` (índice de los documentos del laboratorio: minutas, panel de tareas, manuscrito de Argencon, código de frutas). Los originales están en `referencias/laboratorio/` y su texto en `referencias/laboratorio/texto/`. Leelos antes de interpretar qué pide el laboratorio. Esa carpeta no se sube a git: no la agregues.

## Comandos
```bash
.venv\Scripts\activate        # entorno virtual (Windows)
python ejecutar.py            # flujo completo → outputs/ (~1 min, incluye la sensibilidad)
python -m pytest              # pruebas (unittest, compatibles con pytest)
```

## Arquitectura (ver docs/diseno.md)
- Pipes & Filters: un módulo por etapa en `src/smo/` (repositorio → nodos → tolerancias → redes → seleccion → validacion → visualizacion; los orquesta `pipeline.py`).
- Repository: solo `repositorio.py` toca SQL.
- Strategy: las decisiones abiertas (D1–D10) son parámetros en `config/config.yaml`. No las fijes en el código: agregá una estrategia y una opción en el config.
- `seleccion.pagerank` es una implementación propia y explícita (debe coincidir con `networkx.pagerank`; hay una prueba que lo verifica).

## Convenciones
- Código, comentarios y docstrings en español; nombres sin tildes.
- Cada requerimiento (RF/RNF en `docs/diseno.md`) tiene su prueba. Toda funcionalidad nueva lleva prueba.
- Un cambio de resultados se documenta en `docs/resultados_PMV.md`; una decisión nueva o cambiada, en `docs/decisiones_abiertas.md`.
- No modificar `data/raw/` a mano: la BD curada se regenera con `scripts/construir_bd.py`.

## Git
- `main` es lo que Franco revisó. Trabajá en ramas `claude/<tarea>`.
- Commits chicos con mensaje en español, del tipo "Qué cambió: por qué".
- No hacer push ni merge a `main` sin que Franco lo pida.

## Estado (01/10/2026)
- PMV terminado: 45 nodos (aleación + temple), validación contra Ashby con ρs de 0,71 / 0,72 / 0,61 (ver `docs/resultados_PMV.md`).
- Pendiente: revisar con Lautaro `docs/decisiones_abiertas.md`, completar datos mecánicos (6061, 2024, 5052, 7020…) y llevar los resultados al paper y al póster.
