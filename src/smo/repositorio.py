"""Etapa "Base de datos" del flujo (patrón Repository).

Crea la BD SQLite a partir del Excel curado y ofrece consultas con nombre.
El resto del sistema NO escribe SQL: si mañana la BD cambia (Ti, aceros,
otra estructura), solo se modifica este módulo.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

# Hojas del Excel que son tablas de la BD (LEEME y la vista no lo son)
TABLAS = ["fuente", "serie", "aleacion", "estado", "composicion",
          "prop_fisicas", "prop_mecanicas", "prop_al_puro", "observacion"]


def crear_bd(excel: Path, bd: Path) -> dict[str, int]:
    """Vuelca cada hoja-tabla del Excel curado a SQLite. Devuelve filas por tabla."""
    bd = Path(bd)
    bd.parent.mkdir(parents=True, exist_ok=True)
    bd.unlink(missing_ok=True)
    # 'aleacion' en Excel se lee como número (1050); en la BD es texto
    hojas = pd.read_excel(excel, sheet_name=TABLAS, dtype={"aleacion": str})
    with sqlite3.connect(bd) as con:
        for nombre, df in hojas.items():
            df.to_sql(nombre, con, index=False)
    return {n: len(df) for n, df in hojas.items()}


class RepositorioAleaciones:
    """Acceso de solo lectura a la BD de aleaciones de Al."""

    def __init__(self, bd: Path):
        self.bd = Path(bd)
        if not self.bd.exists():
            raise FileNotFoundError(f"No existe la BD {self.bd}. Ejecutar crear_bd() primero.")

    def _consulta(self, sql: str) -> pd.DataFrame:
        with sqlite3.connect(self.bd) as con:
            return pd.read_sql(sql, con)

    def aleaciones(self) -> pd.DataFrame:
        return self._consulta("SELECT * FROM aleacion")

    def propiedades_fisicas(self) -> pd.DataFrame:
        return self._consulta("SELECT * FROM prop_fisicas")

    def propiedades_mecanicas(self) -> pd.DataFrame:
        return self._consulta("SELECT * FROM prop_mecanicas")

    def composicion(self) -> pd.DataFrame:
        return self._consulta("SELECT * FROM composicion")
