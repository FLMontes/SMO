# SMO — Selección de materiales con redes y PageRank

PMV del proyecto "Gemas"/SMO (PIDTA SeCyT‑UNC 2026, Departamento de Materiales y Tecnología, FCEFyN‑UNC).

Una colección de aleaciones de Al se convierte en una red: cada material es un nodo, y hay una arista por cada atributo en el que dos materiales "se tocan". Para un caso de diseño se arma la sub‑red con los atributos relevantes, PageRank ordena los candidatos y el resultado se compara con el índice de Ashby.

## Cómo correrlo (Windows)

```bash
cd C:\Proyectos\Materiales\SMO
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python ejecutar.py          # flujo completo → carpeta outputs/ (~1 min)
python -m pytest            # 21 pruebas
```

La demo paso a paso está en `notebooks/demo_PMV.ipynb`. Abrila con Jupyter o VS Code.

## Resultados principales

| Caso | Índice de Ashby | Spearman ρs | Top‑5 en común |
|---|---|---|---|
| Tirante liviano y resistente | σy/ρ | 0,71 | 5 de 5 |
| Viga liviana y resistente | σy^(2/3)/ρ | 0,72 | 5 de 5 |
| Viga liviana y rígida | E^(1/2)/ρ | 0,61 | 3 de 5 |

Detalle e interpretación en `docs/resultados_PMV.md`.

## Estructura

```
config/config.yaml      ← TODAS las decisiones abiertas (D1–D10) y los casos de diseño
data/raw/               ← BD curada de aleaciones de Al (Excel)
scripts/construir_bd.py ← cómo se generó esa BD desde el Excel original
src/smo/                ← código (un módulo por etapa del flujo)
  repositorio.py   Excel → SQLite y consultas      (patrón Repository)
  nodos.py         tabla de materiales             (Strategy: granularidad)
  tolerancias.py   vecindades de cada atributo     (Strategy: rango/porcentual/absoluta)
  redes.py         red primaria y primigenia
  seleccion.py     sub-red de trabajo + PageRank
  validacion.py    índices de Ashby, Spearman
  visualizacion.py figuras
  pipeline.py      orquestación                    (Pipes & Filters)
tests/                  ← pruebas (unittest; también corren con pytest)
notebooks/demo_PMV.ipynb
docs/diseno.md          ← problema, requerimientos, arquitectura, patrones, plan
docs/resultados_PMV.md  ← resultados y hallazgos para el paper
docs/decisiones_abiertas.md ← lo que hay que revisar con Lautaro
outputs/                ← rankings (CSV), figuras (PNG), redes (GraphML, se abren con Gephi)
```

## Cómo agregar un caso de diseño

En `config/config.yaml`, dentro de `casos:`:

```yaml
  mi_caso:
    descripcion: "..."
    criterios: {Rp02_MPa: maximizar, alfa_um_mK: minimizar}
    indice_ashby: "Rp02_MPa / alfa_um_mK"
```
