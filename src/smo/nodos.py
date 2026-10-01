"""Etapa "Objetos": arma la tabla de nodos (un material = una fila de atributos).

Decisión abierta D1 (granularidad del nodo), implementada como Strategy:
  - "aleacion_estado": un nodo por aleación + temple (p. ej. 6082-T6).
        Las propiedades mecánicas dependen del temple; las físicas se toman
        de la aleación (D8: E, ρ, α y T sólidus dependen de la composición,
        no del temple).
  - "aleacion": un nodo por aleación, solo con propiedades físicas.
"""
from __future__ import annotations

import warnings

import pandas as pd

from .repositorio import RepositorioAleaciones

COLUMNAS_FISICAS = ["E_GPa", "G_GPa", "poisson", "T_solidus_C", "T_liquidus_C", "cp_J_kgK",
                    "alfa_um_mK", "densidad_kg_m3", "resistividad_nOhm_m", "k_termica_W_mK",
                    "conductividad_IACS"]


def _fisicas_por_aleacion(repo: RepositorioAleaciones) -> pd.DataFrame:
    """Un valor por aleación (promedio entre las filas por estado; en la BD son iguales)."""
    fis = repo.propiedades_fisicas()
    return fis.groupby("aleacion")[COLUMNAS_FISICAS].mean()


def _nodos_aleacion_estado(repo: RepositorioAleaciones, excluir_dudosos: bool) -> pd.DataFrame:
    mec = repo.propiedades_mecanicas()
    if excluir_dudosos:
        mec = mec[mec["dato_dudoso"] == 0]
    df = mec.join(_fisicas_por_aleacion(repo), on="aleacion")
    df["id"] = df["aleacion"] + "-" + df["estado"]
    return df


def _nodos_aleacion(repo: RepositorioAleaciones, excluir_dudosos: bool) -> pd.DataFrame:
    df = _fisicas_por_aleacion(repo).reset_index()
    df["estado"] = None
    df["dato_dudoso"] = 0
    df["id"] = df["aleacion"]
    return df


ESTRATEGIAS = {"aleacion_estado": _nodos_aleacion_estado, "aleacion": _nodos_aleacion}


def construir_nodos(repo: RepositorioAleaciones, granularidad: str, atributos: list[str],
                    excluir_dudosos: bool = True) -> tuple[pd.DataFrame, list[str]]:
    """Devuelve (tabla de nodos indexada por id, atributos realmente usados).

    Se descartan los nodos a los que les falta algún atributo (RF2) y los
    atributos que no existen para la granularidad elegida (p. ej. Rp0,2 si
    el nodo es la aleación sin temple).
    """
    df = ESTRATEGIAS[granularidad](repo, excluir_dudosos)
    usados = [a for a in atributos if a in df.columns]
    for a in set(atributos) - set(usados):
        warnings.warn(f"Atributo {a!r} no disponible con granularidad {granularidad!r}; se omite.")
    series = repo.aleaciones().set_index("aleacion")["serie"]
    df["serie"] = df["aleacion"].map(series)
    antes = len(df)
    df = df.dropna(subset=usados)
    df = df.set_index("id")[["aleacion", "estado", "serie", "dato_dudoso", *usados]]
    df.attrs["descartados_por_datos_incompletos"] = antes - len(df)
    return df.sort_index(), usados
