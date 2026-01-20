import math
from Classes.file_system_manager import FileSystemManager

class FAT_table_manager:

    def __init__(self):
        self.file_sys_manager = FileSystemManager()

    def get_entrada_FAT(self, arquivo, numero_entradas): # pega a posição absoluta de uma entrada FAT livre
        offset_fat = self.file_sys_manager.get_offset("fat1")
        
        entradas = []
        with open(arquivo, 'r+b') as f:
            f.seek(offset_fat)

            posicao = 0

            for i in range(numero_entradas):
                f.seek(posicao)
                entrada_bytes = f.read(4)  # Lê 4 bytes (32 bits) da entrada FAT
                
                if entrada_bytes != 0x00000000:
                    posicao = f.tell()
                else:
                    entradas.append(posicao)
            
        return entradas


    def alocar_arquivo(self, tamanho_arquivo, arquivo):

        # falta alterar o campo 1° cluster da entrada do arquivo no root dir

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()

        quantidade_de_clusters = math.ceil(tamanho_arquivo/tamanho_cluster)
        clusters_alocados = []

        if self.procurar_cluster_livre():
            
            with open(arquivo, 'r+b') as f:
                clusters_alocados.append(self.procurar_cluster_livre())

                for i in range(quantidade_de_clusters-1):
                    cluster = self.procurar_cluster_livre()
                    clusters_alocados.append(cluster)

                # pega as entradas livres necessárias na tabela FAT
                entradas = self.get_entrada_FAT(arquivo, quantidade_de_clusters) 

                for i in range(len(entradas)):
                    posicao = entradas[i]
                    f.seek(posicao)

                    if i == len(entradas)-1:
                        valor = 0xFFFFFFFF  # EOF
                        f.write(valor.to_bytes(4, byteorder='little'))
                    else:
                        valor = entradas[i]
                        f.write(valor.to_bytes(4, byteorder='little'))
                        
        # aloca os clusters dos arquivos na tabela
        return
    
    def desalocar_arquivo(primeiro_cluster):
        # desaloca os clusters de um arquivo alocado na tabela
        return

    def procurar_cluster_livre(self):
        # procura um cluster livre
        return

    def pegar_proximo_cluster():
        # Encontra o proximo cluster de uma chain     
        return

    def sincronizar_fat(primeiro_cluster):
        # Sincroniza as tabelas FAT
        return
    
