import math
from Classes.file_system_manager import FileSystemManager

class FAT_table_manager:

    def __init__(self):
        self.file_sys_manager = FileSystemManager()


    def alocar_arquivo(tamanho_arquivo):

        tamanho_cluster = FileSystemManager.get_tamanho_cluster
        
        quantidade_de_clusters = math((tamanho_arquivo/tamanho_cluster)).ceil

        # aloca os clusters dos arquivos na tabela
        return
    
    def desalocar_arquivo(primeiro_cluster):
        # desaloca os clusters de um arquivo alocado na tabela
        return

    def procurar_entrada_livre():
        # procura um cluster livre
        return

    def pegar_proximo_cluster():
        # Encontra o proximo cluster de uma chain     
        return

    def sincronizar_fat(primeiro_cluster):
        # Sincroniza as tabelas FAT
        return