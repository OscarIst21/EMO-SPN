import os
import sys

# Agregar la ruta del proyecto/src al PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(BASE_DIR)

import unittest
from emo_spn import emo_encrypt, emo_decrypt
from logging_tools import (
    compute_entropy, avalanche_distance,
    plot_histogram, plot_avalanche
)

class TestEmoSPN(unittest.TestCase):

    def setUp(self):
        self.msg = "Hola EMO-SPN"
        self.msg_mod = "Hola EMO-SPL"   # cambia un byte
        self.key = "MiClaveSegura123"

    def test_encrypt_decrypt(self):
        cifrado, _ = emo_encrypt(self.msg, self.key)
        descifrado, _ = emo_decrypt(cifrado, self.key)

        self.assertEqual(descifrado, self.msg,
                         "El descifrado NO coincide con el mensaje original.")

    def test_entropy(self):
        cifrado, _ = emo_encrypt(self.msg, self.key)
        ent = compute_entropy(cifrado)

        self.assertGreater(ent, 5.0,
                           "La entropía es demasiado baja; puede haber patrón.")

    def test_avalanche_effect(self):
        cifrado1, _ = emo_encrypt(self.msg, self.key)
        cifrado2, _ = emo_encrypt(self.msg_mod, self.key)

        # ⚠️ avalanche_distance retorna: bits, pct
        bits, pct = avalanche_distance(cifrado1, cifrado2)

        # efecto avalancha típico ≈ 50%,
        # aquí pedimos mínimo 20% para validación básica
        self.assertGreater(
            pct,
            0.51,
            f"Avalancha insuficiente: {pct*100:.2f}% ({bits} bits cambiados)"
        )

    def test_generate_graphs(self):
        cifrado, _ = emo_encrypt(self.msg, self.key)

        plot_histogram(cifrado)
        plot_avalanche([0.3, 0.5, 0.4])

        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
