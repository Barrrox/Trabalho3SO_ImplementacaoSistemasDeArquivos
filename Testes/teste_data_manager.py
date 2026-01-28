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
        
        offset_dados = self.fsm.get_offset("area_dados")
        lista_clusters = [offset_dados]

        resultado = self.fsm.data_manager.alocar_cluster(lista_clusters, dados)
        
        # Validação do retorno
        self.assertEqual(resultado, ("Clusters alocados com sucesso. Posicoes: ", lista_clusters))

        # Validação física
        with open(self.caminho_particao, "rb") as f:
            f.seek(offset_dados)
            self.assertEqual(f.read(tamanho_cluster), dados)

    def test_alocar_cluster_com_padding(self):
        """Testa se preenche com zeros quando dados < cluster."""
        tamanho_cluster = self.fsm.get_tamanho_cluster()
        dados = b"DADOS_CURTOS"
        
        offset_dados = self.fsm.get_offset("area_dados")
        lista_clusters = [offset_dados]

        self.fsm.data_manager.alocar_cluster(lista_clusters, dados)

        with open(self.caminho_particao, "rb") as f:
            f.seek(offset_dados)
            conteudo = f.read(tamanho_cluster)
            self.assertTrue(conteudo.startswith(dados))
            self.assertEqual(conteudo[len(dados):], b'\x00' * (tamanho_cluster - len(dados)))

    def test_alocar_cluster_multiplos_fragmentados(self):
        """Testa escrita em clusters não contíguos."""
        tamanho_cluster = self.fsm.get_tamanho_cluster()
        dados = b"PARTE1" + (b"\x00" * (tamanho_cluster - 6)) + b"PARTE2" + (b"\x00" * (tamanho_cluster - 6))
        
        offset_dados = self.fsm.get_offset("area_dados")
        # Posição do cluster 0 e do cluster 2 (pulando o 1)
        pos_c0 = offset_dados
        pos_c2 = offset_dados + (tamanho_cluster * 2)
        lista_clusters = [pos_c0, pos_c2]

        self.fsm.data_manager.alocar_cluster(lista_clusters, dados)

        with open(self.caminho_particao, "rb") as f:
            # Verifica Cluster 0
            f.seek(pos_c0)
            self.assertTrue(f.read(tamanho_cluster).startswith(b"PARTE1"))
            
            # Verifica Cluster 2
            f.seek(pos_c2)
            self.assertTrue(f.read(tamanho_cluster).startswith(b"PARTE2"))

if __name__ == '__main__':
    unittest.main()