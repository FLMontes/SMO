"""Pruebas de la validación contra Ashby (RF8) y del flujo completo (RF9)."""
import unittest

import pandas as pd

from smo.validacion import comparar, indice_ashby, spearman


class TestValidacion(unittest.TestCase):
    def test_rf8_indice_manual(self):
        n = pd.DataFrame({"Rp02_MPa": [100.0, 400.0], "densidad_kg_m3": [2700.0, 2800.0]}, index=["a", "b"])
        idx = indice_ashby(n, "Rp02_MPa / densidad_kg_m3")
        self.assertAlmostEqual(idx["b"], 400 / 2800)

    def test_spearman_extremos(self):
        a = pd.Series([1, 2, 3, 4], index=list("wxyz"))
        self.assertAlmostEqual(spearman(a, a * 10), 1.0)
        self.assertAlmostEqual(spearman(a, -a), -1.0)

    def test_comparar_metricas(self):
        rk = pd.DataFrame({"pagerank": [0.5, 0.3, 0.2], "puesto": [1, 2, 3]}, index=list("abc"))
        comp, met = comparar(rk, pd.Series([3.0, 2.0, 1.0], index=list("abc"), name="indice_ashby"), k=2)
        self.assertEqual(met["spearman"], 1.0)
        self.assertEqual(met["top2_coincidencias"], 2)
        self.assertEqual(list(comp["puesto_ashby"]), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
