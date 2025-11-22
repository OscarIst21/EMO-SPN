import os
import sys

# Agregar la ruta del proyecto/src al PYTHONPATH
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.append(BASE_DIR)
from emo_spn import emo_encrypt, emo_decrypt

import unittest
from emo_spn import emo_encrypt, emo_decrypt
from logging_tools import (
    compute_entropy, avalanche_distance,
    plot_histogram, plot_avalanche
)

class TestEmoSPN(unittest.TestCase):

    def setUp(self):
        self.msg = "Hola EMO-SPN"
        self.msg_mod = "Hola EMO-SPL"   # cambia 1 bit lógico
        self.key = "MiClaveSegura123"

    def test_encrypt_decrypt(self):
        cifrado, _ = emo_encrypt(self.msg, self.key)
        descifrado, _ = emo_decrypt(cifrado, self.key)

        self.assertEqual(descifrado, self.msg,
                         "El descifrado NO coincide con el mensaje original.")

    def test_entropy(self):
        cifrado, _ = emo_encrypt(self.msg, self.key)
        ent = compute_entropy(cifrado)

        # en cifrado real: > 6.5 bits por byte
        self.assertGreater(ent, 5.0,
                           "La entropía es demasiado baja; puede haber patrón.")

    def test_avalanche_effect(self):
        cifrado1, _ = emo_encrypt(self.msg, self.key)
        cifrado2, _ = emo_encrypt(self.msg_mod, self.key)

        aval = avalanche_distance(cifrado1, cifrado2)

        # efecto avalancha típico: ~50% de bits cambiados
        self.assertGreater(aval, 0.20,
                           "Avalancha insuficiente; muy pocos bits cambian.")

    def test_generate_graphs(self):
        cifrado, _ = emo_encrypt(self.msg, self.key)

        # genera histogramas (ver carpeta '/output')
        plot_histogram(cifrado)
        plot_avalanche([0.3, 0.5, 0.4])

        # si no explota, pasa
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
