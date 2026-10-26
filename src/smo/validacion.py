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


def spearman(puesto_a: pd.Series, puesto_b: pd.Series) -> float:
    """Correlaciona dos series de puestos, alineadas por identificador."""
    puesto_a, puesto_b = puesto_a.align(puesto_b, join="inner")
    return float(puesto_a.corr(puesto_b))


def comparar(ranking: pd.DataFrame, indice: pd.Series, k: int = 5) -> tuple[pd.DataFrame, dict]:
    """Agrega el índice y su puesto al ranking, y devuelve métricas de acuerdo."""
    df = ranking.join(indice.rename("indice_ashby"), how="inner")
    df["puesto_ashby"] = df["indice_ashby"].rank(ascending=False, method="average")
    top_pr = set(df.nsmallest(k, "puesto").index)
    top_ashby = set(df.nsmallest(k, "puesto_ashby").index)
    metricas = {"n_nodos": len(df),
                "spearman": round(spearman(df["puesto"], df["puesto_ashby"]), 3),
                f"top{k}_coincidencias": len(top_pr & top_ashby),
                "mejor_pagerank": df["puesto"].idxmin(),
                "mejor_ashby": df["puesto_ashby"].idxmin()}
    return df, metricas
