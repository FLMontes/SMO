"""Pruebas de las etapas BD → nodos → tolerancias → redes (RF1–RF5).

Se escriben con unittest (biblioteca estándar) para que corran con
`python -m unittest` aunque no esté pytest; pytest también las ejecuta.
"""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from smo.config import cargar_config
from smo.nodos import construir_nodos
from smo.redes import elementos_aleantes, red_primaria, red_primigenia
from smo.repositorio import RepositorioAleaciones, crear_bd
from smo.tolerancias import calcular_tolerancias

CFG = cargar_config()
ATRIBUTOS = list(CFG["atributos"])


class BaseConBD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.bd = Path(cls.tmp.name) / "test.db"
        cls.filas = crear_bd(CFG["datos"]["excel"], cls.bd)
        cls.repo = RepositorioAleaciones(cls.bd)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()


class TestBD(BaseConBD):
    def test_rf1_tablas_y_filas(self):
        self.assertEqual(self.filas["aleacion"], 34)
        self.assertEqual(self.filas["composicion"], 364)
        self.assertEqual(self.filas["prop_mecanicas"], 49)

    def test_aleacion_es_texto(self):
        self.assertIn("7075", set(self.repo.aleaciones()["aleacion"]))


class TestNodos(BaseConBD):
    def test_rf2_sin_faltantes(self):
        nodos, usados = construir_nodos(self.repo, "aleacion_estado", ATRIBUTOS, True)
        self.assertFalse(nodos[usados].isna().any().any())
        self.assertIn("7075-T6", nodos.index)

    def test_d6_excluye_dudosos(self):
        con, _ = construir_nodos(self.repo, "aleacion_estado", ATRIBUTOS, False)
        sin, _ = construir_nodos(self.repo, "aleacion_estado", ATRIBUTOS, True)
        self.assertIn("5251-O", con.index)
        self.assertNotIn("5251-O", sin.index)

    def test_d1_granularidad_aleacion_omite_rp02(self):
        with self.assertWarns(UserWarning):
            nodos, usados = construir_nodos(self.repo, "aleacion", ATRIBUTOS, True)
        self.assertNotIn("Rp02_MPa", usados)
        self.assertTrue(nodos.index.is_unique)


class TestTolerancias(unittest.TestCase):
    def test_rf3_porcentual_y_absoluta(self):
        n = pd.DataFrame({"x": [100.0, 200.0]}, index=["a", "b"])
        cfg = {"x": {"tolerancia": 0.05}}
        self.assertEqual(list(calcular_tolerancias(n, cfg, ["x"], "porcentual")["x"]), [5.0, 10.0])
        self.assertEqual(list(calcular_tolerancias(n, cfg, ["x"], "absoluta")["x"]), [0.05, 0.05])


class TestRedPrimaria(unittest.TestCase):
    """Caso armado a mano: a=100, b=108, c=130 con tolerancia ±5 %.
    a–b: |8| <= 5+5.4 → arista a→b.   b–c: |22| > 5.4+6.5 → nada.   a–c: nada."""

    def setUp(self):
        self.n = pd.DataFrame({"aleacion": ["A", "B", "C"], "serie": ["1XXX"] * 3,
                               "x": [100.0, 108.0, 130.0], "y": [1.0, 1.0, 5.0]},
                              index=["a", "b", "c"])
        self.t = calcular_tolerancias(self.n, {"x": {"tolerancia": 0.05}, "y": {"tolerancia": 0.01}},
                                      ["x", "y"], "porcentual")
        self.G = red_primaria(self.n, self.t, ["x", "y"])

    def test_rf5_orientacion_creciente(self):
        self.assertTrue(self.G.has_edge("a", "b", key="x"))
        self.assertFalse(self.G.has_edge("b", "a", key="x"))
        self.assertFalse(self.G.has_edge("b", "c", key="x"))

    def test_rf5_valores_iguales_dos_direcciones(self):
        self.assertTrue(self.G.has_edge("a", "b", key="y"))
        self.assertTrue(self.G.has_edge("b", "a", key="y"))

    def test_una_arista_por_atributo(self):
        self.assertEqual(self.G.number_of_edges("a", "b"), 2)   # x e y


class TestRedPrimigenia(BaseConBD):
    def test_rf4_7075(self):
        nodos, _ = construir_nodos(self.repo, "aleacion_estado", ATRIBUTOS, True)
        G = red_primigenia(nodos, self.repo.composicion(), 0.1, "hacia_elemento")
        destinos = {v for _, v in G.out_edges("7075-T6")}
        self.assertTrue({"Zn", "Mg", "Cu", "Al"} <= destinos)
        self.assertNotIn("Fe", destinos)       # Fe solo tiene máximo → impureza
        self.assertEqual(G.nodes["Zn"]["tipo"], "elemento")

    def test_d3_bidireccional_y_ninguna(self):
        nodos, _ = construir_nodos(self.repo, "aleacion_estado", ATRIBUTOS, True)
        comp = self.repo.composicion()
        bi = red_primigenia(nodos, comp, 0.1, "bidireccional")
        self.assertTrue(bi.has_edge("Zn", "7075-T6"))
        self.assertEqual(red_primigenia(nodos, comp, 0.1, "ninguna").number_of_edges(), 0)

    def test_d7_combinados_se_separan(self):
        comp = pd.DataFrame([{"aleacion": "X", "elemento": "Zr+Ti", "pct_min": 0.1, "pct_max": 0.3,
                              "es_balance": 0}])
        self.assertEqual(set(elementos_aleantes(comp, 0.1)["elemento"]), {"Zr", "Ti"})


if __name__ == "__main__":
    unittest.main()
