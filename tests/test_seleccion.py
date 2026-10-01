"""Pruebas de la sub-red de trabajo y PageRank (RF6, RF7)."""
import unittest

import networkx as nx

from smo.seleccion import pagerank, ranking, seleccionar, subred_trabajo


def red_ejemplo():
    """3 materiales en cadena por x (a<b<c) y un elemento."""
    G = nx.MultiDiGraph()
    for n in "abc":
        G.add_node(n, tipo="material", aleacion=n, serie="1XXX")
    G.add_node("Al", tipo="elemento")
    G.add_edge("a", "b", key="x", atributo="x")
    G.add_edge("b", "c", key="x", atributo="x")
    G.add_edge("a", "b", key="y", atributo="y")
    for n in "abc":
        G.add_edge(n, "Al", key="composicion", atributo="composicion")
    return G


class TestSubred(unittest.TestCase):
    def test_rf6_solo_atributos_elegidos(self):
        H = subred_trabajo(red_ejemplo(), {"x": "maximizar"})
        atributos = {d["atributo"] for *_, d in H.edges(data=True)}
        self.assertEqual(atributos, {"x", "composicion"})
        self.assertEqual(H.number_of_nodes(), 4)

    def test_minimizar_invierte(self):
        H = subred_trabajo(red_ejemplo(), {"x": "minimizar"}, incluir_composicion=False)
        self.assertTrue(H.has_edge("b", "a"))
        self.assertFalse(H.has_edge("a", "b"))


class TestPageRank(unittest.TestCase):
    def test_coincide_con_networkx(self):
        for ponderacion in ("uniforme", "por_atributo"):
            H = subred_trabajo(red_ejemplo(), {"x": "maximizar", "y": "maximizar"}, True, ponderacion)
            propio = pagerank(H, 0.85)
            try:
                ref = nx.pagerank(H, alpha=0.85, tol=1e-12, weight="peso")
            except ImportError:                      # networkx usa scipy
                self.skipTest("scipy no instalado")
            for n in H:
                self.assertAlmostEqual(propio[n], ref[n], places=8)

    def test_d9_por_atributo_reparte_igual(self):
        H = subred_trabajo(red_ejemplo(), {"x": "maximizar", "y": "maximizar"}, True, "por_atributo")
        # "a" tiene 1 arista x, 1 arista y, 1 de composición → cada una pesa 1
        self.assertEqual(sorted(d["peso"] for *_, d in H.out_edges("a", data=True)), [1.0, 1.0, 1.0])

    def test_rf7_suma_uno_y_sin_elementos(self):
        G = red_ejemplo()
        r = ranking(G, pagerank(G))
        self.assertAlmostEqual(r["pagerank"].sum(), 1.0)
        self.assertNotIn("Al", r.index)

    def test_maximizar_premia_valor_alto(self):
        r, _ = seleccionar(red_ejemplo(), {"x": "maximizar"}, 0.85, incluir_composicion=False)
        self.assertEqual(r.index[0], "c")
        r, _ = seleccionar(red_ejemplo(), {"x": "minimizar"}, 0.85, incluir_composicion=False)
        self.assertEqual(r.index[0], "a")


if __name__ == "__main__":
    unittest.main()
