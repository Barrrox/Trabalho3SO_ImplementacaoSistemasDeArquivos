import unittest
from unittest.mock import patch, MagicMock

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

    @patch('os.path.exists')
    def test_comando_formatar_caminho_invalido(self, mock_exists):
        """Testa o erro quando o arquivo .bin não existe"""
        mock_exists.return_value = False
        
        retorno_esperado = ["[sys] - Caminho não encontrado"]
        retorno_real = self.file_system_manager.comando_formatar("caminho/fantasma.bin", "512", "8", "512")
        
        self.assertEqual(retorno_real, retorno_esperado)

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('Formatador.formatador.Formatador') 
    def test_comando_formatar_sucesso(self, MockFormatador, mock_getsize, mock_exists):
        """Testa o fluxo completo de formatação com sucesso"""
        # Configuração do cenário
        mock_exists.return_value = True
        mock_getsize.return_value = 2048  # Disco pequeno para teste
        
        # Simula o objeto formatador para não mexer no disco real
        mock_fmt_instance = MockFormatador.return_value
        
        # Execução
        endereco = "disco_virtual.bin"
        retorno = self.file_system_manager.comando_formatar(endereco, "512", "4", "256")
        
        # Verificações
        retorno_esperado = [f"[sys] - Partição em {endereco} formatada com sucesso."]
        self.assertEqual(retorno, retorno_esperado)
        self.assertEqual(self.file_system_manager.get_bytes_por_setor(), 512)
        self.assertEqual(self.file_system_manager.get_setores_por_cluster(), 4)

    def test_comando_deletar_sucesso(self):
        """Testa a deleção de um arquivo com sucesso"""
        # Criamos Mocks para os managers que o comando utiliza
        self.file_system_manager.root_dir_manager = MagicMock()
        self.file_system_manager.fat_manager = MagicMock()
        
        # Simula que o arquivo existe 
        # Formato: [atributo, nome, extensao, tamanho, dono, nivel_de_acesso, primeiro_cluster]
        # O cluster 10 é o que deve ser passado para a FAT
        self.file_system_manager.root_dir_manager.ler_entrada.return_value = [0x00, "teste", "txt", 1024, 1, 1, 10]
        
        # Execução
        nome_arquivo = "teste.txt"
        retorno = self.file_system_manager.comando_deletar(nome_arquivo)
        
        # Verificações
        retorno_esperado = [f"arquivo {nome_arquivo} excluido"]
        self.assertEqual(retorno, retorno_esperado)
        
        # Verifica se os métodos de "limpeza" foram chamados com os dados certos
        self.file_system_manager.fat_manager.desalocar_arquivo.assert_called_once_with(10)
        self.file_system_manager.root_dir_manager.desalocar_entrada.assert_called_once_with(nome_arquivo)
        self.file_system_manager.fat_manager.sincronizar_fat.assert_called_once_with(10)

    def test_comando_deletar_arquivo_nao_encontrado(self):
        """Testa o erro ao tentar deletar um arquivo que não existe no root dir"""
        self.file_system_manager.root_dir_manager = MagicMock()
        
        # Simula que a busca não retornou nada
        self.file_system_manager.root_dir_manager.ler_entrada.return_value = None
        
        retorno = self.file_system_manager.comando_deletar("arquivo_fantasma.bin")
        
        retorno_esperado = ["[sys] - Arquivo não encontrado"]
        self.assertEqual(retorno, retorno_esperado)

if __name__ == "__main__":
    unittest.main()