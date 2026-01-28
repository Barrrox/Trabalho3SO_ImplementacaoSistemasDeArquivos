import unittest
from unittest.mock import MagicMock, patch, mock_open
from Classes.file_system_manager import FileSystemManager
import os
from Testes import TAMANHO_TESTE

class TestRootDirManager(unittest.TestCase):

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

    # Sem entradas FAT suficientes
    def test_buscar_entradas_livres_falha(self):

        # 1. Preencher FAT com entradas mock

        # Descobrir offset da fat
        offset_fat = self.fsm.get_offset("fat1")

        with open(self.caminho_particao, "rb+") as f:
            f.seek(offset_fat + 4) # Pula entrada reservada 0
            
            total_clusters = self.fsm.get_total_clusters()

            # Preenche
            for i in range(1, int(total_clusters)):
                f.write((i + 1).to_bytes(4, "little")) # Escreve 4 bytes

        # 2. Busca entradas livres

        retorno_esperado = ([], "Não há entradas FAT livres suficientes.")

        retorno_real = self.fsm.fat_manager.buscar_entradas_livres(4)

        self.assertEqual(retorno_esperado, retorno_real)

    # Tem entradas suficientes
    def test_buscar_entradas_livres_sucesso(self):
        """
        Preenche os clusters de 1 a 9 e o cluster 14.
        Deve retornar os clusters livres: 10, 11, 12, 15
        """

        # 1. Preencher FAT com entradas mock

        # Descobrir offset da fat
        offset_fat = self.fsm.get_offset("fat1")

        with open(self.caminho_particao, "rb+") as f:
            f.seek(offset_fat + 4)
            
            # Preenche dos clusters 1 a 10
            for i in range(1, 11):
                f.write((i).to_bytes(4, "little")) # Escreve 4 bytes

            # Pula para o cluster 14 e preenche
            f.seek(3*4, 1)
            f.write((15).to_bytes(4, "little")) # Escreve 4 bytes

        # 2. Busca entradas livres
        
        retorno_esperado = ([11, 12, 13, 15], None)

        retorno_real = self.fsm.fat_manager.buscar_entradas_livres(4)

        self.assertEqual(retorno_esperado, retorno_real)


    def test_alocar_entradas_FAT_sucesso_um_cluster(self):
        """Testa a alocação de um único cluster na FAT."""
        tamanho_cluster = self.fsm.get_tamanho_cluster()
        offset_fat = self.fsm.get_offset("fat1")
        
        # Tenta alocar espaço para 1 cluster (ex: arquivo de 500 bytes com cluster de 4KB)
        resultado = self.fsm.fat_manager.alocar_entradas_FAT(500)
        
        # O primeiro cluster livre deve ser o 1 (conforme sua lógica de pular o 0)
        self.assertEqual(resultado, [1])
        
        # Verificação física na FAT
        with open(self.caminho_particao, "rb") as f:
            # Posiciona no índice 1 da FAT (offset_fat + 1*4)
            f.seek(offset_fat + 4)
            entrada = int.from_bytes(f.read(4), 'little')
            # Deve ser EOF (0xFFFFFFFF)
            self.assertEqual(entrada, 0xFFFFFFFF)

    def test_alocar_entradas_FAT_sucesso_multiplos_clusters(self):
        """Testa o encadeamento (chaining) de múltiplos clusters."""
        tamanho_cluster = self.fsm.get_tamanho_cluster()
        offset_fat = self.fsm.get_offset("fat1")
        
        # Aloca 3 clusters (ex: arquivo de 10KB com cluster de 4KB)
        clusters_alocados = self.fsm.fat_manager.alocar_entradas_FAT(1024 * 10)
        
        self.assertEqual(clusters_alocados, [1, 2, 3])
        
        with open(self.caminho_particao, "rb") as f:
            # Cluster 1 deve apontar para o 2
            f.seek(offset_fat + (1 * 4))
            self.assertEqual(int.from_bytes(f.read(4), 'little'), 2)
            
            # Cluster 2 deve apontar para o 3
            f.seek(offset_fat + (2 * 4))
            self.assertEqual(int.from_bytes(f.read(4), 'little'), 3)
            
            # Cluster 3 deve ser EOF
            f.seek(offset_fat + (3 * 4))
            self.assertEqual(int.from_bytes(f.read(4), 'little'), 0xFFFFFFFF)

    def test_alocar_entradas_FAT_fragmentado(self):
        """Testa a alocação quando existem clusters ocupados no meio."""
        offset_fat = self.fsm.get_offset("fat1")
        
        # 1. Simula ocupação: marca o cluster 2 como ocupado manualmente
        with open(self.caminho_particao, "rb+") as f:
            f.seek(offset_fat + (2 * 4))
            f.write((99).to_bytes(4, 'little'))
            
        # 2. Aloca 2 clusters. O sistema deve pular o 2 e usar [1, 3]
        clusters_alocados = self.fsm.fat_manager.alocar_entradas_FAT(512 * 16) # 2 clusters
        
        self.assertEqual(clusters_alocados, [1, 3])
        
        with open(self.caminho_particao, "rb") as f:
            # Cluster 1 deve apontar para o 3
            f.seek(offset_fat + (1 * 4))
            self.assertEqual(int.from_bytes(f.read(4), 'little'), 3)
            
            # Cluster 3 deve ser EOF
            f.seek(offset_fat + (3 * 4))
            self.assertEqual(int.from_bytes(f.read(4), 'little'), 0xFFFFFFFF)

    def test_alocar_entradas_FAT_sem_espaco(self):
        """Testa o comportamento quando o disco está cheio."""
        # Tenta alocar um tamanho absurdamente maior que os 10MB do setUp
        resultado = self.fsm.fat_manager.alocar_entradas_FAT(1024 * 1024 * 100)
        
        # Deve retornar False conforme definido no manager
        self.assertFalse(resultado)

# Testes verificar espaco:
    # arquivo menor que o setor
    # arquivo maior que o setor
    # arquivo com um cluster
    # arquivo com mais de um cluster
    # arquivo maior que o espaço disponivel        

    # def test_verificar_espaco_disponivel_falha(self):

    #     retorno_esparado = False
        
    #     retorno = self.fat_table_manager.verificar_espaco_disponivel(1024*1024*100) # 100 MB


