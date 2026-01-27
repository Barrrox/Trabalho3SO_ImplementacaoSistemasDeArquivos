class data_manager:
    def __init__(self, file_sys_manager):
        self.file_sys_manager = file_sys_manager
        self.disk_manager = file_sys_manager.disk_manager

    # aloca o cluster no arquivo via disk_manager
    # lista de clusters: contém a posição absoluta dos clusters a serem alocados
    # dados == dados a serem escritos no cluster (deve conter os dados em sequência, isto é, sem separação entre clusters)
    def alocar_cluster(self, lista_clusters, dados):

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        numero_de_escritas = len(lista_clusters)

        bytes_escritos = 0 # variável de controle de bytes escritos
        for i in range(numero_de_escritas):
            posicao = lista_clusters[i] # pega a posição absoluta do cluster a ser escrito
            dados_a_escrever = dados[bytes_escritos:(bytes_escritos + tamanho_cluster)] # separa dados com tamanho de 1 cluster

            if len(dados_a_escrever) < tamanho_cluster:
                # se os dados a escrever forem menores que o tamanho do cluster, completa com zeros
                dados_a_escrever += b'\x00' * (tamanho_cluster - len(dados_a_escrever))

            self.disk_manager.escrever_setor(posicao, dados_a_escrever) # manda a requisição de escrita para o disk manager
            bytes_escritos += len(dados_a_escrever) # variável de controle de bytes escritos

        if bytes_escritos != len(dados):
            return print(f"Erro na alocação do cluster. bytes_escritos != len(dados): {bytes_escritos} != {len(dados)}")
        else:
            return ("Clusters alocados com sucesso. Posicoes: ", lista_clusters)

    
    def liberar_cluster():

        return
    
    def ler_dados(clusters_arquivo):
        """
        Lê os dados de um arquivo via disk_manager. Os clusters precisam estar em ordem
        clusters_arquivo: lista com as posições absolutas dos clusters do arquivo a serem lidos
        Retorna: dados lidos do arquivo (byte array)"""

        return dados_arquivo