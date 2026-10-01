"""Orquestación del flujo completo (Pipes & Filters).

    Excel curado → SQLite → nodos → tolerancias → redes → sub-red → PageRank
                 → ranking + validación Ashby + figuras

Uso (desde la carpeta SMO):
    python ejecutar.py                     # con config/config.yaml
    python ejecutar.py --config otra.yaml
"""
from __future__ import annotations

import argparse
import json
import warnings
from copy import deepcopy

import networkx as nx
import pandas as pd

from . import visualizacion as viz
from .config import cargar_config
from .nodos import construir_nodos
from .redes import red_completa, red_primaria, red_primigenia, resumen
from .repositorio import RepositorioAleaciones, crear_bd
from .seleccion import seleccionar
from .tolerancias import calcular_tolerancias
from .validacion import comparar, indice_ashby

FRACCIONES_SENSIBILIDAD = [0.025, 0.05, 0.10, 0.15, 0.20, 0.30]


def construir_red(cfg: dict, repo: RepositorioAleaciones, granularidad: str):
    """Nodos → tolerancias → red primaria + primigenia. Devuelve (nodos, atributos, G)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")      # atributos omitidos: se informan en el resumen
        nodos, usados = construir_nodos(repo, granularidad, list(cfg["atributos"]),
                                        cfg["nodos"]["excluir_dudosos"])
    tol = calcular_tolerancias(nodos, cfg["atributos"], usados, cfg["tolerancias"]["estrategia"],
                               cfg["tolerancias"].get("fraccion_rango", 0.10))
    G = red_completa(red_primaria(nodos, tol, usados),
                     red_primigenia(nodos, repo.composicion(), cfg["primigenia"]["umbral_pct"],
                                    cfg["primigenia"]["orientacion"]))
    return nodos, usados, G


def correr_caso(cfg: dict, repo: RepositorioAleaciones, nombre: str):
    """Ejecuta un caso de diseño. Devuelve (comparación, métricas, sub-red, nodos)."""
    caso = cfg["casos"][nombre]
    gran = caso.get("granularidad", cfg["nodos"]["granularidad"])
    nodos, usados, G = construir_red(cfg, repo, gran)
    faltan = set(caso["criterios"]) - set(usados)
    if faltan:
        raise ValueError(f"Caso {nombre}: atributos {faltan} no disponibles con granularidad {gran}")
    rk, H = seleccionar(G, caso["criterios"], cfg["pagerank"]["alpha"],
                        cfg["pagerank"]["incluir_composicion"], cfg["pagerank"]["ponderacion"])
    comp, met = comparar(rk, indice_ashby(nodos, caso["indice_ashby"]))
    met = {"caso": nombre, "granularidad": gran, **met}
    return comp, met, H, nodos, G


def sensibilidad(cfg: dict, repo: RepositorioAleaciones) -> pd.DataFrame:
    """Spearman vs ancho de vecindad, con y sin red primigenia."""
    filas = []
    for frac in FRACCIONES_SENSIBILIDAD:
        for con_comp in (True, False):
            c = deepcopy(cfg)
            c["tolerancias"]["estrategia"] = "rango"
            c["tolerancias"]["fraccion_rango"] = frac
            c["pagerank"]["incluir_composicion"] = con_comp
            for nombre in c["casos"]:
                _, met, *_ = correr_caso(c, repo, nombre)
                filas.append({"caso": nombre, "fraccion_rango": frac, "incluir_composicion": con_comp,
                              "spearman": met["spearman"], "top5_coincidencias": met["top5_coincidencias"]})
    return pd.DataFrame(filas)


def ejecutar(cfg: dict) -> pd.DataFrame:
    out = cfg["datos"]["salida"]
    out.mkdir(parents=True, exist_ok=True)
    print("1) BD:", crear_bd(cfg["datos"]["excel"], cfg["datos"]["bd"]))
    repo = RepositorioAleaciones(cfg["datos"]["bd"])
    nombres = {a: d["nombre"] for a, d in cfg["atributos"].items()}

    metricas = []
    for nombre, caso in cfg["casos"].items():
        comp, met, H, nodos, G = correr_caso(cfg, repo, nombre)
        metricas.append(met)
        comp.to_csv(out / f"ranking_{nombre}.csv", float_format="%.5f")
        ejes = tuple(caso["criterios"])[::-1]   # x = densidad (2º criterio), y = 1º criterio
        viz.red_sobre_carta(H, comp, nodos, ejes, nombres, caso["descripcion"],
                            out / f"red_{nombre}.png")
        viz.puestos(comp, f"{nombre}: ρs = {met['spearman']}", out / f"puestos_{nombre}.png")
        nx.write_graphml(G, out / f"red_completa_{met['granularidad']}.graphml")
        print(f"2) {nombre}: {met}  red={resumen(G)}")

    tabla = pd.DataFrame(metricas)
    tabla.to_csv(out / "resumen_validacion.csv", index=False)

    sens = sensibilidad(cfg, repo)
    sens.to_csv(out / "sensibilidad.csv", index=False)
    con = sens[sens["incluir_composicion"] == cfg["pagerank"]["incluir_composicion"]]
    viz.sensibilidad(con, out / "sensibilidad.png")
    with open(out / "config_usada.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2, default=str)
    print("3) Resultados en", out)
    return tabla


def main() -> None:
    p = argparse.ArgumentParser(description="SMO: selección de materiales con PageRank")
    p.add_argument("--config", default=None, help="ruta a un config.yaml alternativo")
    args = p.parse_args()
    print(ejecutar(cargar_config(args.config)).to_string(index=False))


if __name__ == "__main__":
    main()
