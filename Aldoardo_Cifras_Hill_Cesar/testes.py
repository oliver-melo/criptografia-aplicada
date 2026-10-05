import unittest

from cifras import cifrar_cesar, cifrar_hill, decifrar_cesar, decifrar_hill


class TesteCesar(unittest.TestCase):
    def test_cifrar_e_decifrar(self):
        cifrado = cifrar_cesar("Casa!", 3)
        self.assertEqual(cifrado, "Fdvd!")
        self.assertEqual(decifrar_cesar(cifrado, 3), "Casa!")

    def test_deslocamento_maior_que_alfabeto(self):
        self.assertEqual(cifrar_cesar("ABC", 27), "BCD")


class TesteHill(unittest.TestCase):
    def test_exemplo_classico(self):
        chave = [[3, 3], [2, 5]]
        self.assertEqual(cifrar_hill("HELP", chave), "HIAT")
        self.assertEqual(decifrar_hill("HIAT", chave), "HELP")

    def test_acentos_e_preenchimento(self):
        chave = [[3, 3], [2, 5]]
        cifrado = cifrar_hill("Olá", chave)
        self.assertEqual(decifrar_hill(cifrado, chave), "OLAX")

    def test_chave_invalida(self):
        with self.assertRaises(ValueError):
            cifrar_hill("TESTE", [[2, 4], [2, 4]])


if __name__ == "__main__":
    unittest.main()
