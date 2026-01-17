import unittest

from Classes.file_system_manager import FileSystemManager

class TesteSystemFileManager(unittest.TestCase):

    def setUp(self):

        self.file_system_manager = FileSystemManager()
        return 
    
    def tearDown(self):
        return 
    
    # ler_input_interface
    def test_ler_input_interface(self):

        # 1. Comando Inexistente
        comandos_teste = [
            "comando_inexistente",
        ]

        retorno_esperado = ("Comando inválido ou não existente! -2")

        for comando_teste in comandos_teste:

            retorno_real = self.file_system_manager.ler_input_interface(comando_teste)

            # self.assertEqual(retorno_esperado, retorno_real)
            self.assertEqual(retorno_esperado, retorno_real)

        # 2. Comando invalido

        comandos_teste = [
            "",
            " ",
            "  ",
            "\n",
        ]
        retorno_esperado = ("Comando inválido ou não existente! -1")

        for comando_teste in comandos_teste:

            retorno_real = self.file_system_manager.ler_input_interface(comando_teste)

            # self.assertEqual(retorno_esperado, retorno_real)
            self.assertEqual(retorno_esperado, retorno_real)

        # 3. Comando válido - Função Exemplo

        comando_teste = "exemplo katchau magrao123"
        retorno_esperado = "Comando de exemplo! você escreveu 'exemplo' seguido de ('katchau', 'magrao123')."

        # Chama a função
        retorno_real = self.file_system_manager.ler_input_interface(comando_teste)

        self.assertEqual(retorno_esperado, retorno_real)


if __name__ == "__main__":
    unittest.main()