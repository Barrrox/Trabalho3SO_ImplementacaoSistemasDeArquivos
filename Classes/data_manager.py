class data_manager:
    def __init__(self, file_sys_manager):
        self.file_sys_manager = file_sys_manager
        self.disk_manager = file_sys_manager.disk_manager

    # aloca o cluster no arquivo via disk_manager
    # lista de clusters: contém a posição absoluta dos clusters a serem alocados
    # dados == dados a serem escritos no cluster (deve conter os dados em sequência, isto é, sem separação entre clusters)

    def split_cluster_in_sectors(self, cluster):
        # Obtém o tamanho do setor
        tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        
        # Divide o cluster em setores
        for i in range(0, len(cluster), tamanho_setor):
            # Recorta o array no tamanho do setor
            setor = cluster[i:i + tamanho_setor]
            # Retorna via yield uma lista contendo os bytes do setor
            yield setor




    def alocar_cluster(self, lista_clusters, dados):
        """
        Docstring for alocar_cluster
        
        :param lista_clusters: lista contendo as posições absolutas dos clusters alocados
        :param dados: bytes a serem escritos, deve ser contínuo (sem separação cluser a cluster)

        :return: print contendo a lista de posições alocadas 
        """

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        numero_de_escritas = len(lista_clusters)

        bytes_escritos = 0 # variável de controle de bytes escritos

        for i in range(numero_de_escritas): # escreve um numero de vezes == ao numero de clusters necessários

            posicao = lista_clusters[i] # pega a posição absoluta do cluster a ser escrito

            quanto_falta_escrever = len(dados) - bytes_escritos

            if quanto_falta_escrever < tamanho_cluster: 
            # caso específico: último cluster a ser escrito não está completo
            # fix -> pegar o tamanho que falta e completar com 0's

                dados_reais = dados[bytes_escritos:]
                padding = tamanho_cluster - len(dados_reais)
                dados_a_escrever = dados_reais + b'\x00' * padding


            else:
                dados_a_escrever = dados[bytes_escritos:(bytes_escritos + tamanho_cluster)] # separa dados com tamanho de 1 cluster

            # separa na quantia de setores necessários para a escrita
            escritas_setor = 0
            posicao_escrita = posicao
            for setor in self.split_cluster_in_sectors(dados_a_escrever):
                
                # escreve no setor
                self.disk_manager.escrever_setor(posicao_escrita, setor) # manda a requisição de escrita para o disk manager
                bytes_escritos += len(setor) # variável de controle de bytes escritos
            
                # ajusta o offset de escrita para a posição do próximo setor
                escritas_setor+=1
                posicao_escrita = posicao + (escritas_setor * self.disk_manager.tamanho_setor)


        if bytes_escritos != len(dados):
            return (f"Erro na alocação do cluster. bytes_escritos != len(dados): {bytes_escritos} != {len(dados)}")
        else:
            return (f"Clusters alocados com sucesso. Posicoes: {lista_clusters}")

    
    def liberar_cluster():

        return
    
    def ler_clusters(self, lista_clusters):
        """
        Docstring for alocar_cluster
        
        :param lista_clusters: lista contendo as posições absolutas dos clusters a serem lidos

        :return lista que contém dados lidos com tamanho de 1 cluster a cada posição 
        """

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        tamanho_setor = self.file_sys_manager.get_tamanho_setor()
        numero_de_leituras = len(lista_clusters)

        dados_arquivo = ""
        dados_lidos = b""
        bytes_lidos = 0 # variável de controle de bytes lidos

        for i in range(numero_de_leituras): # escreve um numero de vezes == ao numero de clusters necessários

            posicao = int(lista_clusters[i]) # pega a posição absoluta do cluster a ser escrito

            for posicao_leitura in range(0, tamanho_cluster, tamanho_setor):
                
                dados_lidos += self.disk_manager.ler_setor(posicao+posicao_leitura)
                bytes_lidos += tamanho_setor
            
            if bytes_lidos == tamanho_cluster:
                dados_arquivo += dados_lidos

            else:
                error = f"[sys] - bytes lidos != tamanho de 1 cluster -> {bytes_lidos} != {tamanho_cluster}"
                return error

        return dados_arquivo