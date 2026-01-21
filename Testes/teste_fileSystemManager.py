import unittest
from unittest.mock import patch, MagicMock
import os

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

        retorno_esperado = ["Comando inválido ou não existente!"]

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
        retorno_esperado = ["Comando inválido ou não existente!"]

        for comando_teste in comandos_teste:

            retorno_real = self.file_system_manager.ler_input_interface(comando_teste)

            # self.assertEqual(retorno_esperado, retorno_real)
            self.assertEqual(retorno_esperado, retorno_real)

        # 3. Comando válido - Função Exemplo

        comando_teste = "exemplo katchau magrao123"
        retorno_esperado = ["Comando de exemplo! você escreveu 'exemplo' seguido de ('katchau', 'magrao123')."]

        # Chama a função
        retorno_real = self.file_system_manager.ler_input_interface(comando_teste)

        self.assertEqual(retorno_esperado, retorno_real)

    @patch('builtins.input')
    @patch('os.path.exists')
    def test_comando_formatar_caminho_invalido(self, mock_exists, mock_input):
        """Testa o erro quando o arquivo .bin não existe"""
        mock_exists.return_value = False
        mock_input.return_value = "caminho/fantasma.bin"
        
        retorno_esperado = ["[sys] - Caminho não encontrado"]
        retorno_real = self.file_system_manager.comando_formatar()
        
        self.assertEqual(retorno_real, retorno_esperado)

    @patch('builtins.input')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_comando_formatar_cancelado(self, mock_getsize, mock_exists, mock_input):
        """Testa se o sistema para quando o usuário digita 'n' na confirmação"""
        mock_exists.return_value = True
        mock_getsize.return_value = 1048576  # 1MB
        # Sequência de inputs: caminho, bytes_setor, setores_cluster, entradas_raiz, confirmação
        mock_input.side_effect = ["disco.bin", "512", "8", "512", "n"]
        
        retorno_esperado = ["[sys] - Formatação cancelada pelo usuário"]
        retorno_real = self.file_system_manager.comando_formatar()
        
        self.assertEqual(retorno_real, retorno_esperado)

    @patch('builtins.input')
    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('Formatador.formatador.Formatador') 
    def test_comando_formatar_sucesso(self, MockFormatador, mock_getsize, mock_exists, mock_input):
        """Testa o fluxo completo de formatação com sucesso"""
        # Configuração do cenário
        mock_exists.return_value = True
        mock_getsize.return_value = 2048  # Disco pequeno para teste
        mock_input.side_effect = ["disco_virtual.bin", "512", "4", "256", "s"]
        
        # Simula o objeto formatador para não mexer no disco real
        mock_fmt_instance = MockFormatador.return_value
        
        # Execução
        retorno = self.file_system_manager.comando_formatar()
        
        # Verificações
        self.assertIsNone(retorno) # Sucesso retorna None no código
        self.assertEqual(self.file_system_manager.get_bytes_por_setor(), 512)
        self.assertEqual(self.file_system_manager.get_setores_por_cluster(), 4)


if __name__ == "__main__":
    unittest.main()