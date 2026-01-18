import unittest

from Classes.file_system_manager import FileSystemManager

class TesteSystemFileManager(unittest.TestCase):

    def setUp(self):

        self.file_system_manager = FileSystemManager()
        return 
    
    def tearDown(self):
        return 
    
    # ler_input_interface
    def test_comando_exemplo2(self):

        # 1. Resposta errada
        retorno_esperado = False

        dict_retorno_real = self.file_system_manager.comando_exemplo2(1234123412)["rodou?"]

        retorno_real = dict_retorno_real

        # self.assertEqual(retorno_esperado, retorno_real)
        self.assertEqual(retorno_esperado, retorno_real)

        # 2. Resposta certa

        retorno_esperado = True

        dict_retorno_real = self.file_system_manager.comando_exemplo2(1)["rodou?"]

        retorno_real = dict_retorno_real

        # self.assertEqual(retorno_esperado, retorno_real)
        self.assertEqual(retorno_esperado, retorno_real)
    


if __name__ == "__main__":
    unittest.main()