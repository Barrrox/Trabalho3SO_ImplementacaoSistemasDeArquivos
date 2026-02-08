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

        caminho_particao = self.file_sys_manager.get_endereco_particao()

        with open(caminho_particao, "r+b") as f:

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
                    resultado_escrita = self.disk_manager.escrever_setor(posicao_escrita, setor, f)
                    
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
        Lê a cadeia de clusters de forma otimizada usando b"".join().
        
        :param lista_clusters: lista com as posições relativas dos clusters.
        :return: bytes contendo os dados concatenados de todos os clusters.
        """
        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        offset_dados = self.file_sys_manager.get_offset("area_dados")
        caminho_particao = self.file_sys_manager.get_endereco_particao()

        # Variavel para acumular os setores numa lista
        # Antes estava sendo feito com += em uma string, mas
        # o python recria variavel toda vez fazendo isso, o que é lento
        buffer_setores = []

        with open(caminho_particao, "rb") as f:
            for cluster_idx in lista_clusters:
                posicao_base = (cluster_idx * tamanho_cluster) + offset_dados 

                # Le setor a setor
                for deslocamento in range(0, tamanho_cluster, tamanho_setor):
                    setor = self.disk_manager.ler_setor(posicao_base + deslocamento, f)
                    buffer_setores.append(setor)

        # join une os bytes do buffer em uma coisa só
        return b"".join(buffer_setores)