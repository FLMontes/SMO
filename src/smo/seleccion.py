"""Metodología de selección: sub-red de trabajo + PageRank (RF6, RF7).

Pasos (manuscrito Argencon, sección "La metodología de selección"):
  1. Los requisitos de diseño dicen qué atributos importan y si se buscan
     valores altos (maximizar) o bajos (minimizar).
  2. De la red completa se extrae la SUB-RED DE TRABAJO: se dejan "vivas" solo
     las aristas de esos atributos (+ las de composición, si las hay).
     Para "minimizar" se invierte la orientación de esas aristas, para que los
     caminantes fluyan hacia los valores BAJOS.
  3. Se asigna un peso a cada arista (decisión D9, "ponderacion"):
       - "uniforme": cada arista pesa 1. Un atributo con muchas vecindades
         superpuestas (p. ej. densidad, que varía poco) arrastra a la mayoría
         de los caminantes.
       - "por_atributo": al salir de un nodo, cada criterio recibe la misma
         probabilidad total, repartida entre sus aristas. Así cada requisito
         de diseño pesa igual, independientemente de cuántos vecinos tenga.
  4. PageRank camina la sub-red y el puntaje de los materiales es el ranking.
"""
from __future__ import annotations

from collections import Counter

import networkx as nx
import pandas as pd

from .redes import COMPOSICION


def subred_trabajo(G: nx.MultiDiGraph, criterios: dict[str, str],
                   incluir_composicion: bool = True,
                   ponderacion: str = "por_atributo") -> nx.MultiDiGraph:
    """Devuelve una red nueva con los mismos nodos, solo las aristas relevantes
    y el atributo de arista "peso" según la ponderación elegida."""
    H = nx.MultiDiGraph()
    H.add_nodes_from(G.nodes(data=True))
    for u, v, k, d in G.edges(keys=True, data=True):
        a = d["atributo"]
        if a == COMPOSICION:
            if incluir_composicion:
                H.add_edge(u, v, key=k, **d)
        elif a in criterios:
            if criterios[a] == "minimizar":
                u, v = v, u
            H.add_edge(u, v, key=k, **d)
    asignar_pesos(H, ponderacion)
    return H


def asignar_pesos(H: nx.MultiDiGraph, ponderacion: str) -> None:
    """Escribe d["peso"] en cada arista (ver D9 arriba)."""
    for u in H:
        salientes = list(H.out_edges(u, keys=True, data=True))
        por_atributo = Counter(d["atributo"] for *_, d in salientes)
        for *_, d in salientes:
            d["peso"] = 1.0 if ponderacion == "uniforme" else 1.0 / por_atributo[d["atributo"]]


def pagerank(G: nx.MultiDiGraph, alpha: float = 0.85, tol: float = 1e-12,
             max_iter: int = 1000) -> dict:
    """PageRank por iteración de potencias, escrito explícitamente para que se
    vea la fórmula del paper:

        G_i = alpha · Σ_{j→i} G_j · w_ji / k_j  +  (1 - alpha) / N   (+ colgantes)

    - w_ji: peso de la arista j→i (atributo "peso"; 1 si no existe).
    - k_j: suma de pesos de las aristas que salen de j (con pesos 1, es la
      cantidad de aristas salientes, como en el paper).
    - alpha: fracción de caminantes que siguen una arista; (1 - alpha) se
      teletransporta a un nodo al azar. En la notación del paper, d = 1 - alpha.
    - Nodos sin aristas de salida ("colgantes", p. ej. los elementos): su
      puntaje se reparte uniformemente (misma convención que networkx).
    Da el mismo resultado que networkx.pagerank (verificado en las pruebas).
    """
    nodos = list(G.nodes)
    N = len(nodos)
    k = {n: G.out_degree(n, weight="peso") for n in nodos}
    entrantes = {n: [(u, d.get("peso", 1.0)) for u, _, d in G.in_edges(n, data=True)] for n in nodos}
    x = {n: 1.0 / N for n in nodos}
    for _ in range(max_iter):
        colgante = alpha * sum(x[n] for n in nodos if k[n] == 0) / N
        nuevo = {n: alpha * sum(x[j] * w / k[j] for j, w in entrantes[n]) + (1 - alpha) / N + colgante
                 for n in nodos}
        if sum(abs(nuevo[n] - x[n]) for n in nodos) < N * tol:
            return nuevo
        x = nuevo
    raise RuntimeError(f"PageRank no convergió en {max_iter} iteraciones")


def ranking(G: nx.MultiDiGraph, puntajes: dict) -> pd.DataFrame:
    """Tabla ordenada solo con materiales (D4: los elementos no se rankean).
    El puntaje se renormaliza para que los materiales sumen 1."""
    filas = [{"id": n, "aleacion": d.get("aleacion"), "serie": d.get("serie"), "pagerank": puntajes[n]}
             for n, d in G.nodes(data=True) if d.get("tipo") == "material"]
    df = pd.DataFrame(filas).set_index("id")
    df["pagerank"] = df["pagerank"] / df["pagerank"].sum()
    df = df.sort_values("pagerank", ascending=False)
    df["puesto"] = range(1, len(df) + 1)
    return df


def seleccionar(G: nx.MultiDiGraph, criterios: dict[str, str], alpha: float,
                incluir_composicion: bool = True,
                ponderacion: str = "por_atributo") -> tuple[pd.DataFrame, nx.MultiDiGraph]:
    """Atajo: sub-red de trabajo → PageRank → ranking."""
    H = subred_trabajo(G, criterios, incluir_composicion, ponderacion)
    return ranking(H, pagerank(H, alpha)), H
