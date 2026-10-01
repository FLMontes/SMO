"""Lectura y validación de config/config.yaml.

Todas las decisiones abiertas del proyecto (D1..D8 en docs/diseno.md) viven en
ese archivo. Este módulo lo lee, valida los valores y resuelve rutas relativas
respecto de la raíz del proyecto.
"""
from __future__ import annotations

from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[2]          # carpeta SMO/
CONFIG_DEFECTO = RAIZ / "config" / "config.yaml"

OPCIONES = {
    ("nodos", "granularidad"): {"aleacion_estado", "aleacion"},
    ("tolerancias", "estrategia"): {"porcentual", "absoluta"},
    ("primigenia", "orientacion"): {"hacia_elemento", "bidireccional", "ninguna"},
}


def cargar_config(ruta: str | Path | None = None) -> dict:
    """Lee el YAML, valida opciones y convierte rutas de 'datos' en absolutas."""
    ruta = Path(ruta) if ruta else CONFIG_DEFECTO
    with open(ruta, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    validar_config(cfg)
    for clave in ("excel", "bd", "salida"):
        p = Path(cfg["datos"][clave])
        cfg["datos"][clave] = p if p.is_absolute() else RAIZ / p
    return cfg


def validar_config(cfg: dict) -> None:
    """Falla temprano y con un mensaje claro si la configuración es inválida."""
    for (seccion, clave), validas in OPCIONES.items():
        valor = cfg[seccion][clave]
        if valor not in validas:
            raise ValueError(f"{seccion}.{clave} = {valor!r}; opciones válidas: {sorted(validas)}")
    alpha = cfg["pagerank"]["alpha"]
    if not 0 < alpha < 1:
        raise ValueError(f"pagerank.alpha debe estar en (0, 1); vale {alpha}")
    for nombre, caso in cfg["casos"].items():
        for atributo, sentido in caso["criterios"].items():
            if atributo not in cfg["atributos"]:
                raise ValueError(f"Caso {nombre}: atributo {atributo!r} no está en 'atributos'")
            if sentido not in ("maximizar", "minimizar"):
                raise ValueError(f"Caso {nombre}: sentido {sentido!r} debe ser maximizar|minimizar")
