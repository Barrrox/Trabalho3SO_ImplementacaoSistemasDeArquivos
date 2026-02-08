class data_manager:
    """
    Gere as operações de leitura e escrita física de bytes na área de dados do disco.
    """
    def __init__(self, file_sys_manager):
        """
        :param file_sys_manager: Instância do gestor para acesso a offsets e geometria do disco.
        """
        self.file_sys_manager = file_sys_manager
        self.disk_manager = file_sys_manager.disk_manager

    # aloca o cluster no arquivo via disk_manager
    # lista de clusters: contém a posição absoluta dos clusters a serem alocados
    # dados == dados a serem escritos no cluster (deve conter os dados em sequência, isto é, sem separação entre clusters)

    def split_cluster_in_sectors(self, cluster):
        """
        Divide um bloco de cluster em fatias correspondentes ao tamanho de um setor.
        :param cluster: bytes do cluster
        :return: yield bytes do setor
        """
        # Obtém o tamanho do setor
        tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        
        # Divide o cluster em setores
        for i in range(0, len(cluster), tamanho_setor):
            # Recorta o array no tamanho do setor
            setor = cluster[i:i + tamanho_setor]
            # Retorna via yield uma lista contendo os bytes do setor
            yield setor

    def alocar_cluster(self, lista_clusters, dados, callback=None):
        """        
        :param lista_clusters: lista contendo as posições relativas dos clusters alocados
        :param dados: bytes a serem escritos, deve ser contínuo (sem separação cluster a cluster)
        :return: contendo a lista de posições alocadas ou mensagem de erro
        """

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        numero_de_escritas = len(lista_clusters)
        offset_dados = self.file_sys_manager.get_offset("area_dados")
        bytes_escritos = 0 # variável de controle de bytes escritos

        for i in range(numero_de_escritas): # escreve um numero de vezes == ao numero de clusters necessários

            # pega a posição relativa do cluster a ser escrito (Endereço físico)
            posicao = (lista_clusters[i] * tamanho_cluster) + offset_dados 

            quanto_falta_escrever = len(dados) - bytes_escritos

            if quanto_falta_escrever < tamanho_cluster: 
                # caso específico: último cluster a ser escrito não está completo
                # fix -> pegar o tamanho que falta e completar com 0's (padding)

                dados_reais = dados[bytes_escritos:]
                padding = tamanho_cluster - len(dados_reais)
                dados_a_escrever = dados_reais + b'\x00' * padding

            else:
                # separa dados com tamanho de 1 cluster
                dados_a_escrever = dados[bytes_escritos:(bytes_escritos + tamanho_cluster)] 

            # separa na quantia de setores necessários para a escrita
            escritas_setor = 0
            posicao_escrita = posicao
            
            for setor in self.split_cluster_in_sectors(dados_a_escrever):
                
                # escreve no setor
                resultado_escrita = self.disk_manager.escrever_setor(posicao_escrita, setor)
                
                if resultado_escrita is False:
                    return f"[sys] Falha física ao escrever no setor {posicao_escrita}"
                
                bytes_escritos += len(setor) # variável de controle de bytes escritos
            
                # ajusta o offset de escrita para a posição do próximo setor
                escritas_setor += 1
                posicao_escrita = posicao + (escritas_setor * tamanho_setor)
            
            if callback:
                percentual = ((i + 1) / numero_de_escritas) * 100
                callback(percentual) # Notifica a interface

        if bytes_escritos < len(dados):
            return f"Erro na alocação do cluster. bytes_escritos != len(dados): {bytes_escritos} != {len(dados)}"
        else:
            return lista_clusters

    def liberar_cluster():
        return
    
    def ler_clusters(self, lista_clusters):
        """        
        :param lista_clusters: lista contendo as posições relativas dos clusters a serem lidos
        :return: lista que contém dados lidos com tamanho de 1 cluster a cada posição 
        """

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        numero_de_leituras = len(lista_clusters)

        dados_arquivo = b""
        offset_dados = self.file_sys_manager.get_offset("area_dados")
        
        for i in range(numero_de_leituras): # lê um numero de vezes == ao numero de clusters necessários

            bytes_lidos = 0 # variável de controle de bytes lidos
            dados_lidos = b""

            # pega a posição relativa do cluster a ser lido (Endereço físico)
            posicao = (lista_clusters[i] * tamanho_cluster) + offset_dados 

            for posicao_leitura in range(0, tamanho_cluster, tamanho_setor):
                
                dados_lidos += self.disk_manager.ler_setor(posicao + posicao_leitura)
                bytes_lidos += tamanho_setor
            
            if bytes_lidos == tamanho_cluster:
                dados_arquivo += dados_lidos
            else:
                error = f"[sys] - bytes lidos != tamanho de 1 cluster -> {bytes_lidos} != {tamanho_cluster}"
                return error

        return dados_arquivo