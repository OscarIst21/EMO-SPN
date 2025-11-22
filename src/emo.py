import argparse
import unittest
import sys
from emo_spn import emo_encrypt, emo_decrypt

def run_tests():
    print("Ejecutando pruebas automáticas...\n")
    loader = unittest.TestLoader()
    suite = loader.discover("../tests", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="CLI para EMO-SPN")
    parser.add_argument("command", choices=["encrypt", "decrypt", "test"],
                        help="Comando a ejecutar")

    parser.add_argument("--msg", help="Mensaje a cifrar/descifrar")
    parser.add_argument("--key", help="Clave usada")

    args = parser.parse_args()

    if args.command == "test":
        run_tests()
        return

    if args.command == "encrypt":
        cifrado, _ = emo_encrypt(args.msg, args.key)
        print(cifrado.hex())
        return

    if args.command == "decrypt":
        data = bytes.fromhex(args.msg)
        dec, _ = emo_decrypt(data, args.key)
        print(dec)
        return


if __name__ == "__main__":
    main()
