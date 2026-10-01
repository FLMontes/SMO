"""Figuras para el póster / paper (RF9).

1. red_sobre_carta: la sub-red de trabajo dibujada sobre los ejes de la carta
   de Ashby de los dos criterios (p. ej. ρ vs Rp0,2). Tamaño e intensidad del
   nodo = puntaje PageRank. Une las dos ideas del proyecto en una imagen.
2. puestos: puesto PageRank vs puesto Ashby (la diagonal es acuerdo perfecto).
3. sensibilidad: Spearman en función del ancho de vecindad.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import pandas as pd  # noqa: E402

# Paleta de referencia (skill dataviz): slots categóricos 1–3 y tintas de texto
AZUL, NARANJA, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA_2, GRILLA = "#0b0b0b", "#52514e", "#e4e3df"
CATEGORICOS = [AZUL, NARANJA, AQUA]


def _estilo(ax, titulo: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA)
    ax.set_xlabel(xlabel, color=TINTA_2)
    ax.set_ylabel(ylabel, color=TINTA_2)
    ax.tick_params(colors=TINTA_2, labelsize=8)
    ax.grid(color=GRILLA, linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRILLA)


def red_sobre_carta(H: nx.MultiDiGraph, comparacion: pd.DataFrame, nodos: pd.DataFrame,
                    ejes: tuple[str, str], nombres: dict, titulo: str, salida: Path,
                    etiquetas: int = 5) -> Path:
    x, y = ejes
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    pos = {n: (nodos.at[n, x], nodos.at[n, y]) for n in nodos.index}
    for u, v, d in H.edges(data=True):
        if u in pos and v in pos and d["atributo"] in ejes:
            ax.annotate("", xy=pos[v], xytext=pos[u],
                        arrowprops=dict(arrowstyle="-|>", color="#b9b8b2", lw=0.5,
                                        shrinkA=4, shrinkB=4, mutation_scale=6))
    pr = comparacion["pagerank"]
    tam = 30 + 900 * (pr - pr.min()) / (pr.max() - pr.min())
    alfa = 0.35 + 0.65 * (pr - pr.min()) / (pr.max() - pr.min())
    for n in comparacion.index:
        ax.scatter(*pos[n], s=tam[n], color=AZUL, alpha=float(alfa[n]),
                   edgecolors="white", linewidths=2, zorder=3)
    destacados = set(comparacion.nsmallest(etiquetas, "puesto").index)
    for n in destacados:
        ax.annotate(f"{n} (#{comparacion.at[n, 'puesto']})", pos[n], xytext=(6, 6),
                    textcoords="offset points", fontsize=8, color=TINTA, zorder=4)
    mejor_ashby = comparacion["indice_ashby"].idxmax()
    ax.annotate(f"mejor Ashby: {mejor_ashby}", pos[mejor_ashby], xytext=(6, -12),
                textcoords="offset points", fontsize=8, color=TINTA_2, style="italic", zorder=4)
    _estilo(ax, titulo, nombres[x], nombres[y])
    ax.text(0.0, -0.13, "Tamaño del nodo = puntaje PageRank · flechas = aristas de la sub-red de trabajo",
            transform=ax.transAxes, fontsize=8, color=TINTA_2)
    fig.tight_layout()
    fig.savefig(salida)
    plt.close(fig)
    return salida


def puestos(comparacion: pd.DataFrame, titulo: str, salida: Path) -> Path:
    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    n = len(comparacion)
    ax.plot([1, n], [1, n], color=GRILLA, lw=2, zorder=1)
    ax.scatter(comparacion["puesto_ashby"], comparacion["puesto"], s=40, color=AZUL,
               edgecolors="white", linewidths=2, zorder=3)
    for idx in comparacion.nsmallest(3, "puesto_ashby").index:
        ax.annotate(idx, (comparacion.at[idx, "puesto_ashby"], comparacion.at[idx, "puesto"]),
                    xytext=(5, 3), textcoords="offset points", fontsize=8, color=TINTA)
    _estilo(ax, titulo, "Puesto según índice de Ashby", "Puesto según PageRank")
    ax.invert_xaxis(); ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(salida)
    plt.close(fig)
    return salida


def sensibilidad(df: pd.DataFrame, salida: Path) -> Path:
    """df con columnas: caso, fraccion_rango, spearman (una línea por caso)."""
    fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
    finales = []
    for color, (caso, g) in zip(CATEGORICOS, df.groupby("caso", sort=False)):
        g = g.sort_values("fraccion_rango")
        ax.plot(g["fraccion_rango"], g["spearman"], color=color, lw=2, marker="o", ms=5,
                markeredgecolor="white", label=caso)
        finales.append([g["spearman"].iloc[-1], caso, g["fraccion_rango"].iloc[-1]])
    # etiquetas directas al final de cada línea, separadas si quedan muy juntas
    finales.sort()
    for i in range(1, len(finales)):
        finales[i][0] = max(finales[i][0], finales[i - 1][0] + 0.06)
    for y, caso, x in finales:
        ax.annotate(caso, (x, y), xytext=(6, 0), textcoords="offset points",
                    fontsize=8, color=TINTA, va="center", annotation_clip=False)
    ax.set_ylim(top=max(1.0, finales[-1][0] + 0.05))
    ax.axhline(0, color=TINTA_2, lw=0.8)
    _estilo(ax, "Acuerdo con Ashby según el ancho de vecindad",
            "Vecindad (fracción del rango del atributo)", "Spearman ρs")
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_xlim(right=df["fraccion_rango"].max() * 1.6)
    fig.tight_layout()
    fig.savefig(salida)
    plt.close(fig)
    return salida
