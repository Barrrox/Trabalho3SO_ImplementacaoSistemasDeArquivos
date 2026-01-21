from Classes.file_system_manager import FileSystemManager
from Formatador.formatador import Formatador
from Classes.disk_manager import disk_manager

class data_manager:
    def __init__(self):
        self.file_sys_manager = FileSystemManager()
        self.formatador = Formatador()
        self.disk_manager = disk_manager()
    
    def procurar_cluster_livre(self, arquivo, n_clusters,):
        posicao_clusters = []
        offset = self.formatador.get_offset("area_dados")

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        setores_por_cluster = self.file_sys_manager.get_setores_por_cluster()


        with open(arquivo, 'r+b') as f:
            f.seek(offset)

            for i in n_clusters: # para cada cluster necessário
                estado_cluster = f.read(tamanho_cluster) # lê o tamaho de 1 cluster
                if estado_cluster == b'\x00' * tamanho_cluster: # se todos os bytes forem 0, o cluster está livre
                    posicao_clusters.append(offset + (i * tamanho_cluster) ) # salva a posição absoluta do cluster

                else: # se não, como o f.read já desloca o cursor, basta pular para a próxima iteração
                    pass  


        if len(posicao_clusters) == n_clusters:
            return posicao_clusters, None
        else:
            return posicao_clusters, print("Erro, não há clusters livres suficientes. Lista incompleta em anexo")
    

    # aloca o cluster no arquivo via disk_manager
    # envia a lista de clusters a serem alocados
    # dados == dados a serem escritos no cluster (deve conter os dados em sequência, isto é, sem separação entre clusters)
    def alocar_cluster(self, arquivo, lista_clusters, dados):

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        bytes_escritos = 0

        with open(arquivo, 'r+b') as f:

        return
    
    def liberar_cluster():

        return