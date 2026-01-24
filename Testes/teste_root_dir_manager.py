import unittest
from unittest.mock import MagicMock, patch, mock_open
from Classes.root_dir_manager import root_dir_manager

class TestRootDirManager(unittest.TestCase):

    def setUp(self):
        # Mock do FileSystemManager
        self.mock_fsm = MagicMock()
        self.mock_fsm.get_offset.return_value = 1024
        self.mock_fsm.get_endereco_particao.return_value = "disco_fake.bin"
        self.mock_fsm.get_num_entradas_raiz.return_value = 2
        
        self.manager = root_dir_manager(self.mock_fsm)

    @patch("builtins.open", new_callable=mock_open)
    def test_ler_entrada_sucesso(self, mock_file):
        # Cria uma entrada fake de 22 bytes
        # Atrib(0x02), Nome("teste   "), Ext("txt"), Tam(500), Dono(1), Nivel(1), Cluster(5)
        entrada_fake = (
            b'\x02' +               # Atributo
            b'teste   ' +           # Nome (8 bytes)
            b'txt' +                # Extensão (3 bytes)
            (500).to_bytes(4, 'little') +   # Tamanho
            (1).to_bytes(2, 'little') +     # Dono
            (1).to_bytes(2, 'little') +     # Nível
            (5).to_bytes(2, 'little')       # Cluster
        )
        
        mock_file.return_value.read.side_effect = [entrada_fake, b'\x00'*22]

        resultado = self.manager.ler_entrada("teste", "txt")
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado[1], "teste")
        self.assertEqual(resultado[3], 500) # Tamanho
        self.assertEqual(resultado[6], 5)   # Primeiro Cluster

    @patch("builtins.open", new_callable=mock_open)
    def test_ler_entrada_nao_encontrada(self, mock_file):
        # Simula disco vazio (primeiro byte 0x00)
        mock_file.return_value.read.return_value = b'\x00' * 22
        
        resultado = self.manager.ler_entrada("inexistente", "bin")
        self.assertIsNone(resultado)

if __name__ == "__main__":
    unittest.main()