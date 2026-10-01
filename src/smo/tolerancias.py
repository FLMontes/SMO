"""Vecindades ("anchos de caja") de cada atributo de cada nodo — decisión D2.

La tolerancia t es el semiancho de la vecindad: el nodo ocupa [v - t, v + t].
Dos nodos se "tocan" en un atributo si |v1 - v2| <= t1 + t2.

Estrategias (Strategy):
  - "porcentual": t = fracción · |v|   (p. ej. 0.05 → ±5 % del valor)
  - "absoluta":   t = valor fijo en las unidades del atributo

Como t se calcula POR NODO, se cumple el pedido de la minuta del 05/06/2026
(tolerancias individuales, no uniformes). Cuando haya tolerancias de la
fuente (rangos min–max), alcanza con agregar una estrategia nueva acá.
"""
from __future__ import annotations

import pandas as pd


def _porcentual(valores: pd.Series, parametro: float) -> pd.Series:
    return valores.abs() * parametro


def _absoluta(valores: pd.Series, parametro: float) -> pd.Series:
    return pd.Series(parametro, index=valores.index, dtype=float)


ESTRATEGIAS = {"porcentual": _porcentual, "absoluta": _absoluta}


def calcular_tolerancias(nodos: pd.DataFrame, atributos_cfg: dict, atributos: list[str],
                         estrategia: str) -> pd.DataFrame:
    """Devuelve un DataFrame (mismo índice que nodos) con la tolerancia de cada atributo."""
    funcion = ESTRATEGIAS[estrategia]
    tol = pd.DataFrame(index=nodos.index)
    for a in atributos:
        tol[a] = funcion(nodos[a].astype(float), float(atributos_cfg[a]["tolerancia"]))
        if (tol[a] <= 0).any():
            raise ValueError(f"Tolerancia no positiva en {a}")
    return tol
