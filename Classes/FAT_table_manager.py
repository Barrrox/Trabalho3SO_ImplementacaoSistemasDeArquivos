import math
from Classes.file_system_manager import FileSystemManager
from Classes.data_manager import data_manager
from Classes.root_dir_manager import root_dir_manager

class FAT_table_manager:

    def __init__(self):
        self.file_sys_manager = FileSystemManager()
        self.data_manager = data_manager()
        self.root_manager = root_dir_manager()

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

        clusters_alocados = [] # separa a quantia de clusters livres necessários para o arquivo
        clusters_alocados, __Error = self.data_manager.procurar_cluster_livre(quantidade_de_clusters)
       
        if __Error == None: # se tem clusters livres 
    
            with open(arquivo, 'r+b') as f:
                
                # pega as entradas livres necessárias na tabela FAT
                entradas = self.get_entrada_FAT(arquivo, quantidade_de_clusters) 

                for i in range(len(entradas)): # posiciona o cursor na posição absoluta da entrada FAT
                    posicao = entradas[i]
                    f.seek(posicao)

                    if i == len(entradas)-1: # se for o final da chain marca como EOF
                        valor = 0xFFFFFFFF  # EOF
                        f.write(valor.to_bytes(4, byteorder='little'))
                    else: # se nao for o final da chain aponta para o próximo cluster
                        valor = entradas[i]
                        f.write(valor.to_bytes(4, byteorder='little'))
        else:
            return print("Não há clusters livres suficientes para alocar o arquivo.")
                        
        # aloca os clusters dos arquivos na tabela

        # chama o root dir manager para alterar a entrada do arquivo no root dir
        self.root_manager.escrever_entrada(arquivo, clusters_alocados[0]) # nao implementado

        # chama o data manager para alocar os clusters no arquivo
        self.data_manager.alocar_cluster(clusters_alocados, arquivo)




        return
    
    def desalocar_arquivo(primeiro_cluster):
        # desaloca os clusters de um arquivo alocado na tabela
        return

    def pegar_proximo_cluster():
        # Encontra o proximo cluster de uma chain     
        return

    def sincronizar_fat(primeiro_cluster):
        # Sincroniza as tabelas FAT
        return
    
