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
        puestos = pd.Series([1, 2, 3, 4], index=list("wxyz"))
        self.assertAlmostEqual(spearman(puestos, puestos), 1.0)
        self.assertAlmostEqual(spearman(puestos, pd.Series([4, 3, 2, 1], index=puestos.index)), -1.0)

    def test_comparar_metricas(self):
        rk = pd.DataFrame({"pagerank": [0.5, 0.3, 0.2], "puesto": [1, 2, 3]}, index=list("abc"))
        comp, met = comparar(rk, pd.Series([3.0, 2.0, 1.0], index=list("abc"), name="indice_ashby"), k=2)
        self.assertEqual(met["spearman"], 1.0)
        self.assertEqual(met["top2_coincidencias"], 2)
        self.assertEqual(list(comp["puesto_ashby"]), [1, 2, 3])

    def test_comparar_correlaciona_puestos_no_puntajes(self):
        rk = pd.DataFrame({
            "pagerank": [0.5, 0.3, 0.2],
            "puesto": [1, 2, 3],
        }, index=list("abc"))
        indice = pd.Series([1000.0, 100.0, 10.0], index=list("abc"))

        comp, met = comparar(rk, indice)

        self.assertEqual(list(comp["puesto_ashby"]), [1, 2, 3])
        self.assertEqual(met["spearman"], 1.0)

    def test_comparar_usa_solo_materiales_compartidos(self):
        rk = pd.DataFrame({
            "pagerank": [0.5, 0.3, 0.2],
            "puesto": [1, 2, 3],
        }, index=list("abc"))
        indice = pd.Series([5.0, 4.0], index=list("ab"))

        comp, met = comparar(rk, indice, k=1)

        self.assertEqual(list(comp.index), list("ab"))
        self.assertEqual(met["n_nodos"], 2)


if __name__ == "__main__":
    unittest.main()
