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
        numero_de_escritas = len(lista_clusters)

        bytes_escritos = 0 # variável de controle de bytes escritos
        for i in range(numero_de_escritas):
            posicao = lista_clusters[i] # pega a posição absoluta do cluster a ser escrito
            dados_a_escrever = dados[bytes_escritos:(bytes_escritos + tamanho_cluster)] # separa dados com tamanho de 1 cluster

            if len(dados_a_escrever) < tamanho_cluster:
                # se os dados a escrever forem menores que o tamanho do cluster, completa com zeros
                dados_a_escrever += b'\x00' * (tamanho_cluster - len(dados_a_escrever))

            self.disk_manager.escrever_setor(arquivo, posicao, dados_a_escrever) # manda a requisição de escrita para o disk manager
            bytes_escritos += len(dados_a_escrever) # variável de controle de bytes escritos

        if bytes_escritos != len(dados):
            return print(f"Erro na alocação do cluster. bytes_escritos != len(dados): {bytes_escritos} != {len(dados)}")
        else:
            return ("Clusters alocados com sucesso. Posicoes: ", lista_clusters)

    
    def liberar_cluster():

        return