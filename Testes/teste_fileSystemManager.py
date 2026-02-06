import unittest
from unittest.mock import patch, MagicMock
from Testes import TAMANHO_TESTE
import os

from Classes.file_system_manager import FileSystemManager

class TesteSystemFileManager(unittest.TestCase):

    def setUp(self):

        self.file_system_manager = FileSystemManager()
        self.data_manager = self.file_system_manager.data_manager
        self.root_manager = self.file_system_manager.root_dir_manager
        self.fat_manager = self.file_system_manager.fat_manager

        self.caminho_particao = "disco_teste_fsm.bin"
        self.tamanho_teste = TAMANHO_TESTE

        with open(self.caminho_particao, 'wb') as f:
            f.seek(self.tamanho_teste - 1)
            f.write(b'\x00')

        self.file_system_manager.comando_formatar(self.caminho_particao, "512", "8", "512")
        return 
    
    def tearDown(self):
        if os.path.exists(self.caminho_particao):
            os.remove(self.caminho_particao)
        return 
    
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

    def test_fluxo_alocacao(self):
        """
        Testa o fluxo completo de alocação. Roda um for que realiza a operação 3 vezes.

        DataManager.alocar_cluster -> FAT.alocar_entradas -> RootDir.escrever_entrada.
        """

        for i in range(1):

            dados = b'A' * self.file_system_manager.get_tamanho_cluster()
            
            tamanho_arquivo = len(dados)

            clusters_livres, _ = self.fat_manager.buscar_entradas_livres(1)

            #print(clusters_livres)

            self.fat_manager.alocar_entradas_FAT(tamanho_arquivo)


            clusters_alocados = self.data_manager.alocar_cluster(clusters_livres, dados)

            atributo = 0x02 # Arquivo
            nome = f"arq{i}"
            extensao = "txt"
            tamanho = tamanho_arquivo
            primeiro_cluster = clusters_alocados[0]
            dono = 0
            nivel_de_acesso = 0

            retorno = self.root_manager.escrever_entrada_arquivo(atributo, nome, extensao, tamanho, primeiro_cluster, dono, nivel_de_acesso)
    
            # print(f"Retorno escrever_entrada_arquivo: {retorno}")  

            # print(f"len clusters_alocados = {len(clusters_alocados)}")  
            dados_lidos = self.data_manager.ler_clusters(clusters_alocados)

            # print(f"Retorno ler_clusters: {len(dados_lidos)}")
            # print()

        self.assertEqual(dados_lidos, dados)

    def test_funcao_copiar_interna(self):
        """
        Teste de integração: Copia um arquivo de fora do sistema de arquivos para dentro do disco virtual.
        Verifica se a entrada no Root Dir foi criada e se o tamanho confere.
        """

        # 1. Preparação: Criar um arquivo físico no Windows/Linux para ser a origem
        caminho_externo = "arqteste.txt"
        conteudo_original = b"Conteudo de teste para integracao real"
        with open(caminho_externo, "wb") as f:
            f.write(conteudo_original)

        
        try:
            # 2. Execução: Chama a função
            self.file_system_manager.funcao_copiar_interna(caminho_externo)

            # 3. Validação no Root Directory real
            # Extraímos o nome para buscar no manager
            nome_arquivo = caminho_externo[:8]
            extensao = caminho_externo[-3:]

            # print(f"nome_arquivo: {nome_arquivo}")
            # print(f"extensao: {extensao}")
            
            entrada = self.root_manager.ler_entrada(nome_arquivo, extensao)
            # print(f"entrada: {entrada}")
            # Verificações
            self.assertIsNotNone(entrada, "O arquivo deveria ter sido criado no Root Directory.")
            self.assertEqual(entrada[1].strip(), nome_arquivo, "O nome gravado no Root Dir está incorreto.")
            self.assertEqual(entrada[3], len(conteudo_original), "O tamanho gravado diverge do arquivo original.")
            
        finally:
            # Limpeza do arquivo de origem externo
            if os.path.exists(caminho_externo):
                os.remove(caminho_externo)

    def test_copiar_arquivo_inexistente_no_os(self):
        """Verifica o comportamento da função ao tentar copiar um arquivo que não existe no SO."""
        caminho_fantasma = "nao_existir_no_disco.xyz"
        
        resultado = self.file_system_manager.comando_copiar(caminho_fantasma)
        self.assertEqual(resultado, ["[sys] - Arquivo de origem não encontrado"])

    def test_copiar_duplicado_real(self):
        """Verifica se o sistema impede a cópia de um arquivo com nome idêntico já presente no disco."""
        caminho_origem = "oyamada.txt"
        with open(caminho_origem, "wb") as f:
            f.write(b"dados")

        try:
            # Primeira cópia (Sucesso esperado)
            self.file_system_manager.funcao_copiar_interna(caminho_origem)
            
            # Segunda cópia (Deve retornar erro conforme a lógica do manager)
            resultado = self.file_system_manager.funcao_copiar_interna(caminho_origem)
            
            self.assertEqual(resultado, ["[sys] - Arquivo já existe no sistema. Operação abortada"])
            
        finally:
            if os.path.exists(caminho_origem):
                os.remove(caminho_origem)


    def test_funcao_copiar_externa_sucesso(self):
        """
        Teste de integração: Extrai um arquivo do sistema de arquivos para o SO real.
        Verifica se o conteúdo extraído é idêntico ao que estava gravado no binário.
        """
        # 1. Preparação Manual (Injetando um arquivo no disco virtual)
        nome = "externo"
        extensao = "txt"
        conteudo_original = b"Dados guardados dentro do sistema de arquivos FAT48"
        len_conteudo_original = len(conteudo_original)
        caminho_destino_os = "arquivo_extraido.txt"

        # Alocamos espaço e gravamos manualmente para garantir que o dado está lá
        entradas_fat = self.fat_manager.alocar_entradas_FAT(len(conteudo_original))
        self.data_manager.alocar_cluster(entradas_fat, conteudo_original)
        self.root_manager.escrever_entrada_arquivo(2, nome, extensao, len(conteudo_original), entradas_fat[0], dono=0, nivel_de_acesso=0)

        try:
            # 2. Execução: Copia de DENTRO para FORA
            # O caminho de origem deve simular o path que o seu sistema espera
            caminho_interno = f"{nome}.{extensao}" 
            self.file_system_manager.funcao_copiar_externa(caminho_interno, caminho_destino_os)

            # 3. Validação
            self.assertTrue(os.path.exists(caminho_destino_os), "O arquivo não foi criado no sistema operacional.")
            
            with open(caminho_destino_os, "rb") as f:
                conteudo_extraido = f.read()
            
            secao_extraida = conteudo_extraido[0:len_conteudo_original]

            self.assertEqual(secao_extraida, conteudo_original)

        finally:
            # Limpeza do arquivo criado no SO
            if os.path.exists(caminho_destino_os):
                os.remove(caminho_destino_os)

    def test_copiar_externa_arquivo_inexistente(self):
        """Verifica se a função retorna o erro correto ao tentar extrair um arquivo que não existe no binário."""
        caminho_interno = "arqteste.txt"
        caminho_destino = "saida_falha.txt"

        # Execução
        resultado = self.file_system_manager.funcao_copiar_externa(caminho_interno, caminho_destino)

        # Validação
        self.assertEqual(resultado, ["[sys] - Arquivo de origem não encontrado"], "A função deveria retornar erro de arquivo não encontrado.")
        self.assertFalse(os.path.exists(caminho_destino), "Um arquivo não deveria ter sido criado no SO para uma origem inexistente.")
            


if __name__ == "__main__":
    unittest.main()