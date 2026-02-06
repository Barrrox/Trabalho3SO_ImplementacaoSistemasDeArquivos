import unittest
from Classes.file_system_manager import FileSystemManager
import os
from Testes import TAMANHO_TESTE

class TestFatTableManager(unittest.TestCase):

    def setUp(self):
        
        self.fsm = FileSystemManager()
        
        self.caminho_particao = "disco_teste_root_dir.bin"
        self.tamanho_teste = TAMANHO_TESTE

        with open(self.caminho_particao, 'wb') as f:
            f.seek(self.tamanho_teste - 1)
            f.write(b'\x00')

        self.fsm.comando_formatar(self.caminho_particao, "512", "8", "512")
        return
    
    def tearDown(self):
        if os.path.exists(self.caminho_particao):
            os.remove(self.caminho_particao)
        return
    
    import unittest
import os
from Classes.file_system_manager import FileSystemManager

class TestDataManager(unittest.TestCase):

    def setUp(self):
        self.fsm = FileSystemManager()
        self.caminho_particao = "disco_teste_data.bin"
        self.tamanho_teste = 1024 * 1024 * 1 # 1 MB para agilidade
        
        # Cria arquivo binário vazio
        with open(self.caminho_particao, 'wb') as f:
            f.truncate(self.tamanho_teste)

        # Formata: 512 bytes/setor, 8 setores/cluster (4KB/cluster), 512 entradas raiz
        self.fsm.comando_formatar(self.caminho_particao, "512", "8", "512")

    def tearDown(self):
        if os.path.exists(self.caminho_particao):
            os.remove(self.caminho_particao)

    def test_alocar_cluster_tamanho_exato(self):
        """Testa escrita de 1 cluster completo."""
        tamanho_cluster = self.fsm.get_tamanho_cluster()
        dados = b"A" * tamanho_cluster
        #print(f"tamanho_cluster: {tamanho_cluster}")
        
        #print(f"len(dados): {len(dados)}")
        
        lista_clusters = [1]

        resultado = self.fsm.data_manager.alocar_cluster(lista_clusters, dados)
        
        #print(f"resultado alocar_cluster: {resultado}")
        # Validação do retorno
        self.assertEqual(resultado, lista_clusters)

        # Validação física
        with open(self.caminho_particao, "rb") as f:
    
            dados_lidos = self.fsm.data_manager.ler_clusters(lista_clusters)
            self.assertEqual(dados_lidos, dados)

            

    def test_alocar_cluster_com_padding(self):
        """Testa se preenche com zeros quando dados < cluster."""
        tamanho_cluster = self.fsm.get_tamanho_cluster()
        dados = b"DADOS_CURTOS"
        
        offset_dados = self.fsm.get_offset("area_dados")
        lista_clusters = [1]

        self.fsm.data_manager.alocar_cluster(lista_clusters, dados)

        with open(self.caminho_particao, "rb") as f:
            f.seek(offset_dados)
            conteudo = self.fsm.data_manager.ler_clusters(lista_clusters)
            self.assertTrue(conteudo.startswith(dados))
            self.assertEqual(conteudo[len(dados):], b'\x00' * (tamanho_cluster - len(dados)))

    def test_alocar_cluster_multiplos_fragmentados(self):
        """Testa escrita em clusters não contíguos."""
       
        dados1 = b"PARTE1"
        dados2 = b"PARTE2"

        # Posição do cluster 1 e do cluster 3 (pulando o 2)
        pos_c1 = 1
        pos_c3 = 5
        
        self.fsm.data_manager.alocar_cluster([pos_c1], dados1)
        self.fsm.data_manager.alocar_cluster([pos_c3], dados2)

        with open(self.caminho_particao, "rb") as f:
            
            # Verifica Cluster 1
            dados_lidos = self.fsm.data_manager.ler_clusters([pos_c1])
            #print(dados_lidos[0:10])
            self.assertTrue(dados_lidos.startswith(b"PARTE1"))
            
            # Verifica Cluster 3
            dados_lidos = self.fsm.data_manager.ler_clusters([pos_c3])
            #print(dados_lidos[0:10])
            self.assertTrue(dados_lidos.startswith(b"PARTE2"))

    def test_ler_clusters_sucesso(self):
        """Testa se a leitura de clusters retorna os dados gravados anteriormente."""
        tamanho_cluster = self.fsm.get_tamanho_cluster()
        # Dados de teste: 1 cluster completo
        dados_originais = b"DADOS_PARA_LEITURA" + (b"0" * (tamanho_cluster - 18))
        
        offset_dados = self.fsm.get_offset("area_dados")
        lista_clusters = [offset_dados]

        # 1. Escreve os dados primeiro
        self.fsm.data_manager.alocar_cluster(lista_clusters, dados_originais)

        # 2. Tenta ler os dados de volta
        dados_lidos = self.fsm.data_manager.ler_clusters(lista_clusters)

        # 3. Validação
        self.assertEqual(dados_lidos, dados_originais, "Os dados lidos são diferentes dos dados gravados.")

if __name__ == '__main__':
    unittest.main()