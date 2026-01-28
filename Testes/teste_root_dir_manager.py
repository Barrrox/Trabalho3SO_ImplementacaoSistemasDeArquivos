import unittest
import os
from Classes.file_system_manager import FileSystemManager

class TestRootDirManager(unittest.TestCase):

    def setUp(self):
        # 1. Instancia o Orquestrador
        self.fsm = FileSystemManager()
        
        # 2. Configura o arquivo de disco virtual real
        self.caminho_particao = "disco_teste_root.bin"
        self.tamanho_teste = 1024 * 1024 # 1 MB
        
        with open(self.caminho_particao, 'wb') as f:
            f.truncate(self.tamanho_teste)

        # 3. Formata para garantir Boot Record e offsets corretos
        # 512 bytes/setor, 8 setores/cluster, 512 entradas no Root Dir
        self.fsm.comando_formatar(self.caminho_particao, "512", "8", "512")
        
        # Atalho para o manager testado
        self.manager = self.fsm.root_dir_manager

    def tearDown(self):
        if os.path.exists(self.caminho_particao):
            os.remove(self.caminho_particao)

    def test_escrever_e_ler_entrada_sucesso(self):
        """Testa o ciclo completo: escrever uma entrada e recuperá-la."""
        # Dados da entrada (22 bytes na arquitetura FAT48)
        # Atrib(0x02), Nome("doc"), Ext("txt"), Tam(1024), Cluster(10), Dono(1), Nivel(1)
        self.manager.escrever_entrada_arquivo(
            atributo=0x02, 
            nome="doc", 
            extensao="txt", 
            tamanho=1024, 
            primeiro_cluster=10, 
            dono=1, 
            nivel_de_acesso=1
        )

        # Tenta ler a entrada criada
        resultado = self.manager.ler_entrada("doc", "txt")
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado[1], "doc")      # Nome
        self.assertEqual(resultado[2], "txt")      # Extensão
        self.assertEqual(resultado[3], 1024)       # Tamanho
        self.assertEqual(resultado[6], 10)         # Primeiro Cluster

    def test_ler_entrada_nao_encontrada(self):
        """Garante que retorna None para arquivos inexistentes."""
        resultado = self.manager.ler_entrada("fake", "csv")
        self.assertIsNone(resultado)

    def test_procurar_entrada_livre_posicao_correta(self):
        """Valida se o buscador de entradas livres retorna o offset correto."""
        offset_inicial = self.fsm.get_offset("root_dir")
        
        # Como o disco está recém formatado, a primeira entrada livre deve ser o próprio offset inicial
        posicao_livre = self.manager.procurar_entrada_livre()
        self.assertEqual(posicao_livre, offset_inicial)

    def test_desalocar_entrada_arquivo(self):
        """Verifica se a exclusão marca o atributo como 0x01."""
        # 1. Escreve
        self.manager.escrever_entrada_arquivo(0x02, "deletar", "tmp", 100, 2, 1, 1)
        
        # 2. Deleta
        sucesso = self.manager.desalocar_entrada_arquivo("deletar")
        self.assertTrue(sucesso)
        
        # 3. Tenta ler (deve retornar None pois ler_entrada ignora 0x01)
        resultado = self.manager.ler_entrada("deletar", "tmp")
        self.assertIsNone(resultado)

    def test_listar_entradas_vazia_e_com_dados(self):
        """Testa a listagem de diretório."""
        # Inicialmente vazio
        self.assertEqual(len(self.manager.listar_entradas()), 0)

        # Adiciona dois arquivos
        self.manager.escrever_entrada_arquivo(0x02, "file1", "dat", 50, 3, 1, 1)
        self.manager.escrever_entrada_arquivo(0x02, "file2", "dat", 60, 4, 1, 1)
        
        lista = self.manager.listar_entradas()
        self.assertEqual(len(lista), 2)
        self.assertEqual(lista[0][0], "file1")
        self.assertEqual(lista[1][0], "file2")

if __name__ == "__main__":
    unittest.main()