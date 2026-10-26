"""Vecindades ("anchos de caja") de cada atributo de cada nodo — decisión D2.

La tolerancia t es el semiancho de la vecindad: el nodo ocupa [v - t, v + t].
Dos nodos se "tocan" en un atributo si |v1 - v2| <= t1 + t2.

Estrategias:
  - "rango":      t = fracción · (máx − mín del atributo en la colección).
        Normaliza atributos con dispersiones y unidades distintas (vuelve
        comparables E, que varía ~6 %, y Rp0,2, que varía ~15 veces).
        Responde a la discusión de la minuta del 14/04/2026 sobre "bolas" en
        espacios con unidades diferentes. Es la que mejor reproduce a Ashby
        (ver outputs/sensibilidad.csv).
  - "porcentual": t = fracción · |v|   (p. ej. 0.05 → ±5 % del valor), por nodo.
  - "absoluta":   t = valor fijo en las unidades del atributo.

"porcentual" calcula t POR NODO (pedido de la minuta del 05/06/2026). Cuando
haya tolerancias de la fuente (rangos min–max por nodo), alcanza con agregar
una estrategia nueva acá.
"""
from __future__ import annotations

import pandas as pd


def _rango(valores: pd.Series, parametro: float) -> pd.Series:
    return pd.Series(parametro * (valores.max() - valores.min()), index=valores.index, dtype=float)


def _porcentual(valores: pd.Series, parametro: float) -> pd.Series:
    return valores.abs() * parametro


def _absoluta(valores: pd.Series, parametro: float) -> pd.Series:
    return pd.Series(parametro, index=valores.index, dtype=float)


ESTRATEGIAS = {"rango": _rango, "porcentual": _porcentual, "absoluta": _absoluta}


def calcular_tolerancias(nodos: pd.DataFrame, atributos_cfg: dict, atributos: list[str],
                         estrategia: str, fraccion_rango: float = 0.10) -> pd.DataFrame:
    """Devuelve un DataFrame (mismo índice que nodos) con la tolerancia de cada atributo.

    Para "rango" se usa fraccion_rango (igual para todos los atributos); para
    "porcentual"/"absoluta", el valor 'tolerancia' de cada atributo en config.yaml.
    """
    funcion = ESTRATEGIAS[estrategia]
    tol = pd.DataFrame(index=nodos.index)
    for a in atributos:
        param = fraccion_rango if estrategia == "rango" else float(atributos_cfg[a]["tolerancia"])
        tol[a] = funcion(nodos[a].astype(float), param)
        if (tol[a] <= 0).any():
            raise ValueError(f"Tolerancia no positiva en {a}")
    return tol
