"""Etapa "Red": construcción de las redes de materiales con networkx.

Se usan MultiDiGraph (grafo dirigido con aristas múltiples) porque, según la
minuta del 05/06/2026, cada sobrelape de vecindad es UNA arista propia: dos
materiales pueden quedar unidos por varias aristas, una por atributo. Así la
sub-red de trabajo puede "apagar" aristas de atributos no relevantes.

Cada arista guarda el atributo "atributo" (p. ej. "Rp02_MPa" o "composicion").
Cada nodo guarda "tipo" ("material" o "elemento").
"""
from __future__ import annotations

from itertools import combinations

import networkx as nx
import pandas as pd

COMPOSICION = "composicion"


def red_primaria(nodos: pd.DataFrame, tol: pd.DataFrame, atributos: list[str]) -> nx.MultiDiGraph:
    """Red de atributos: una arista por cada atributo cuyas vecindades se sobrelapan.

    Orientación: del valor menor al mayor (minutas). Si los valores son iguales
    no hay orden: se agregan las dos direcciones.
    """
    G = nx.MultiDiGraph()
    for nid, fila in nodos.iterrows():
        G.add_node(nid, tipo="material", aleacion=fila["aleacion"], serie=fila["serie"],
                   **{a: float(fila[a]) for a in atributos})
    for i, j in combinations(nodos.index, 2):
        for a in atributos:
            vi, vj = nodos.at[i, a], nodos.at[j, a]
            if abs(vi - vj) <= tol.at[i, a] + tol.at[j, a]:
                if vi < vj:
                    G.add_edge(i, j, key=a, atributo=a)
                elif vj < vi:
                    G.add_edge(j, i, key=a, atributo=a)
                else:
                    G.add_edge(i, j, key=a, atributo=a)
                    G.add_edge(j, i, key=a, atributo=a)
    return G


def elementos_aleantes(composicion: pd.DataFrame, umbral_pct: float) -> pd.DataFrame:
    """Filas (aleacion, elemento, contenido_pct) de los elementos aleantes (D7).

    Un elemento es aleante si la norma le fija un MÍNIMO (los que solo tienen
    máximo, "≤0,40", son impurezas toleradas) y su contenido nominal
    (punto medio del rango) es >= umbral_pct. El Al (balance) siempre lo es.
    Elementos combinados ("Zr+Ti") se separan; "Otros" se ignora.
    """
    filas = []
    for _, r in composicion.iterrows():
        if str(r["elemento"]).startswith("Otros"):
            continue
        if r["es_balance"] == 1:
            filas.append((r["aleacion"], r["elemento"], None))
            continue
        if pd.isna(r["pct_min"]):
            continue
        nominal = r["pct_min"] if pd.isna(r["pct_max"]) else (r["pct_min"] + r["pct_max"]) / 2
        if nominal >= umbral_pct:
            for el in str(r["elemento"]).split("+"):
                filas.append((r["aleacion"], el.strip(), float(nominal)))
    return pd.DataFrame(filas, columns=["aleacion", "elemento", "contenido_pct"])


def red_primigenia(nodos: pd.DataFrame, composicion: pd.DataFrame, umbral_pct: float,
                   orientacion: str) -> nx.MultiDiGraph:
    """Red de composición: material → elemento de aleación (decisión D3).

    "hacia_elemento": la aleación "cita" al elemento (minutas 05 y 12/06/2026).
    "bidireccional": además elemento → aleación (los caminantes pueden pasar
        entre aleaciones que comparten aleantes).
    "ninguna": no se agregan aristas de composición.
    """
    G = nx.MultiDiGraph()
    G.add_nodes_from(nodos.index, tipo="material")
    if orientacion == "ninguna":
        return G
    aleantes = elementos_aleantes(composicion, umbral_pct)
    for nid, fila in nodos.iterrows():
        for _, r in aleantes[aleantes["aleacion"] == fila["aleacion"]].iterrows():
            el = r["elemento"]
            G.add_node(el, tipo="elemento")
            G.add_edge(nid, el, key=COMPOSICION, atributo=COMPOSICION)
            if orientacion == "bidireccional":
                G.add_edge(el, nid, key=COMPOSICION, atributo=COMPOSICION)
    return G


def red_completa(primaria: nx.MultiDiGraph, primigenia: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Superpone la red de atributos sobre la primigenia (mismos nodos-material)."""
    return nx.compose(primigenia, primaria)


def resumen(G: nx.MultiDiGraph) -> dict:
    """Conteo de nodos por tipo y de aristas por atributo."""
    tipos = pd.Series(dict(G.nodes(data="tipo"))).value_counts().to_dict()
    aristas = pd.Series([d["atributo"] for *_, d in G.edges(data=True)]).value_counts().to_dict()
    return {"nodos": tipos, "aristas": aristas}
