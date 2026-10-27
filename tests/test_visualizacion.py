"""Pruebas de las figuras generadas."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from smo.visualizacion import _anotar_sin_solapamiento, puestos, red_sobre_carta, sensibilidad


class TestVisualizacion(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_etiquetas_no_se_solapan(self):
        fig, ax = plt.subplots(figsize=(5, 4))
        etiquetas = [
            (f"Aleacion-{i}", (0.5, 0.5), {})
            for i in range(5)
        ]

        _anotar_sin_solapamiento(ax, etiquetas)

        fig.canvas.draw()
        cajas = [texto.get_window_extent(fig.canvas.get_renderer()) for texto in ax.texts]
        for i, caja in enumerate(cajas):
            for otra in cajas[i + 1:]:
                self.assertFalse(caja.overlaps(otra))

    def test_figuras_sin_titulos_ni_pie(self):
        with tempfile.TemporaryDirectory() as temporal, patch("smo.visualizacion.plt.close"):
            carpeta = Path(temporal)
            indice = ["A-1", "B-2", "C-3"]
            nodos = pd.DataFrame({"x": [1.0, 1.01, 1.02], "y": [2.0, 2.01, 2.02]},
                                 index=indice)
            comparacion = pd.DataFrame({
                "pagerank": [0.6, 0.3, 0.1],
                "puesto": [1, 2, 3],
                "indice_ashby": [3.0, 2.0, 1.0],
                "puesto_ashby": [1, 2, 3],
            }, index=indice)
            red_sobre_carta(nx.MultiDiGraph(), comparacion, nodos, ("x", "y"),
                            {"x": "Eje X", "y": "Eje Y"}, carpeta / "red.png")
            puestos(comparacion, carpeta / "puestos.png")
            sensibilidad(pd.DataFrame({
                "caso": ["A", "A", "B", "B"],
                "fraccion_rango": [0.05, 0.1, 0.05, 0.1],
                "spearman": [0.8, 0.9, 0.7, 0.85],
            }), carpeta / "sensibilidad.png")

            figuras = [plt.figure(numero) for numero in plt.get_fignums()]
            self.assertEqual(len(figuras), 3)
            for figura in figuras:
                ax = figura.axes[0]
                self.assertEqual(ax.get_title(), "")
                self.assertFalse(any("Tamaño del nodo" in texto.get_text() for texto in ax.texts))
                figura.canvas.draw()
                cajas = [texto.get_window_extent(figura.canvas.get_renderer()) for texto in ax.texts]
                for i, caja in enumerate(cajas):
                    for otra in cajas[i + 1:]:
                        self.assertFalse(caja.overlaps(otra))
            self.assertTrue(all((carpeta / nombre).is_file()
                                for nombre in ("red.png", "puestos.png", "sensibilidad.png")))


if __name__ == "__main__":
    unittest.main()
