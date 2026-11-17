"""Testes unitários de lógica numérica, sem substituir imagens da base na avaliação."""
import unittest
import numpy as np
from main import alinhar_busca_local, avaliar, iou


class Algoritmos(unittest.TestCase):
    def test_translacao_sad_ssd(self):
        rng = np.random.default_rng(7)
        referencia = rng.integers(0, 256, (70, 70), dtype=np.uint8)
        # Apenas uma translação matemática para verificar o sinal de dx/dy.
        teste = np.zeros_like(referencia)
        teste[2:, 1:] = referencia[:-2, :-1]
        for metodo in ("sad", "ssd"):
            _, _, dx, dy, _ = alinhar_busca_local(referencia, teste, raio=3, passo=1, metodo=metodo)
            self.assertEqual((dx, dy), (-1, -2))

    def test_iou(self):
        self.assertAlmostEqual(iou((0, 0, 10, 10), (0, 0, 10, 10)), 1)
        self.assertEqual(iou((0, 0, 10, 10), (12, 12, 20, 20)), 0)

    def test_outra_classe_conta_fp(self):
        det = [{"bbox": (10, 10, 20, 20)}]
        gt = [{"bbox": (10, 10, 20, 20), "classe": 2}]
        self.assertEqual(avaliar(det, gt), (0, 1, 0))

    def test_casamento_unico(self):
        det = [{"bbox": (0, 0, 10, 10)}, {"bbox": (0, 0, 10, 10)}]
        gt = [{"bbox": (0, 0, 10, 10), "classe": 4}]
        self.assertEqual(avaliar(det, gt), (1, 1, 0))


if __name__ == "__main__":
    unittest.main()
