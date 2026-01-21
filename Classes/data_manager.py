from Classes.file_system_manager import FileSystemManager
from Formatador.formatador import Formatador

class data_manager:
    def __init__(self):
        self.file_sys_manager = FileSystemManager()
        self.formatador = Formatador()
    
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
            return posicao_clusters
        else:
            return None, print("Erro, não há clusters livres suficientes. Lista incompleta em anexo"), posicao_clusters
    
    def alocar_cluster():

        return
    
    def liberar_cluster():

        return