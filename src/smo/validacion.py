"""Validación contra el método de Ashby (RF8).

Para cada caso de diseño se calcula el índice de desempeño de Ashby
(p. ej. M = σy/ρ) y se compara su ranking con el de PageRank:

- Spearman ρs: correlación entre puestos (1 = mismo orden, 0 = sin relación,
  −1 = orden inverso). Se calcula como Pearson sobre los rangos, sin scipy.
- Coincidencias top-k: cuántos de los k mejores según Ashby aparecen también
  entre los k mejores según PageRank.

Esto responde a la conclusión del manuscrito ("no tenemos una forma de validar
la metodología"): Ashby funciona como referencia conocida.
"""
from __future__ import annotations

import pandas as pd


def indice_ashby(nodos: pd.DataFrame, expresion: str) -> pd.Series:
    """Evalúa la expresión del índice (nombres de columna de la tabla de nodos)."""
    return nodos.eval(expresion).astype(float).rename("indice_ashby")


def spearman(a: pd.Series, b: pd.Series) -> float:
    a, b = a.align(b, join="inner")
    return float(a.rank().corr(b.rank()))


def comparar(ranking: pd.DataFrame, indice: pd.Series, k: int = 5) -> tuple[pd.DataFrame, dict]:
    """Agrega el índice y su puesto al ranking, y devuelve métricas de acuerdo."""
    df = ranking.join(indice)
    df["puesto_ashby"] = df["indice_ashby"].rank(ascending=False, method="min").astype(int)
    top_pr = set(df.nsmallest(k, "puesto").index)
    top_ashby = set(df.nsmallest(k, "puesto_ashby").index)
    metricas = {"n_nodos": len(df),
                "spearman": round(spearman(df["pagerank"], df["indice_ashby"]), 3),
                f"top{k}_coincidencias": len(top_pr & top_ashby),
                "mejor_pagerank": df.index[0],
                "mejor_ashby": df["indice_ashby"].idxmax()}
    return df, metricas
