import unittest
from unittest.mock import MagicMock, patch, mock_open
from Classes.file_system_manager import FileSystemManager
import os

class TestRootDirManager(unittest.TestCase):

    def setUp(self):
        
        self.fsm = FileSystemManager()
        
        self.caminho_particao = "disco_teste_root_dir.bin"
        self.tamanho_teste = 1024 * 1024 * 10 # 10 MB
        # self.tamanho_teste = 1024 * 1024 * 1024 * 4 # 4 GB

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
            f.seek(offset_fat)
            
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
            f.seek(offset_fat)
            
            # Preenche dos clusters 1 a 10
            for i in range(1, 11):
                f.write((i + 1).to_bytes(4, "little")) # Escreve 4 bytes

            # Pula para o cluster 14 e preenche
            f.seek(3*4, 1)
            f.write((15).to_bytes(4, "little")) # Escreve 4 bytes

        # 2. Busca entradas livres
        
        retorno_esperado = ([11, 12, 13, 15], None)

        retorno_real = self.fsm.fat_manager.buscar_entradas_livres(4)

        self.assertEqual(retorno_esperado, retorno_real)

# Testes verificar espaco:
    # arquivo menor que o setor
    # arquivo maior que o setor
    # arquivo com um cluster
    # arquivo com mais de um cluster
    # arquivo maior que o espaço disponivel        

    # def test_verificar_espaco_disponivel_falha(self):

    #     retorno_esparado = False
        
    #     retorno = self.fat_table_manager.verificar_espaco_disponivel(1024*1024*100) # 100 MB


