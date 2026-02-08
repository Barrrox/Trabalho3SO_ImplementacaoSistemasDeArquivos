import math

class FAT_table_manager:

    def __init__(self, file_sys_manager):
        """
        Gerencia a File Allocation Table (FAT), controlando quais clusters estão livres,
        alocados ou pertencem a uma cadeia de um arquivo.
        
        :param file_sys_manager: Instância do FileSystemManager para acessar configurações globais.
        """
        self.file_sys_manager = file_sys_manager
        self.data_manager = file_sys_manager.data_manager
        self.root_manager = file_sys_manager.root_dir_manager
        self.tamanho_entrada = 4 # Cada entrada na FAT ocupa 4 bytes
        self.FAT_EOF = 0xFFFFFFFF


    def verificar_espaco_disponivel(self, tamanho_arquivo):      
        
        """
        Verifica se há clusters livres suficientes na tabela FAT para comportar o arquivo.

        :param tamanho_arquivo: Tamanho total do arquivo em bytes.
        :return: bool: True se houver espaço disponível, False caso contrário.
        """

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        quantidade_de_clusters_necessarios = math.ceil(tamanho_arquivo / tamanho_cluster)
        
        entradas, error = self.buscar_entradas_livres(quantidade_de_clusters_necessarios)

        if error:
            return False

        else:   
            return True

    def buscar_entradas_livres(self, numero_entradas): # pega a posição relativa de uma entrada FAT livre
        """
        Varre a tabela FAT em busca de entradas marcadas como livres (valor 0).

        :param numero_entradas: Quantidade de clusters necessários.
        :return: entradas: lista com os índices (posições relativas) dos clusters livres.
        :return: error: String contendo mensagem de erro ou None se sucesso.
        """

        endereco_particao = self.file_sys_manager.get_endereco_particao()
        
        entradas = []
        with open(endereco_particao, 'rb') as f:
            
            # Começa da entrada 1, ignorando a entrada reservada 0
            f.seek(self.file_sys_manager.get_offset("fat1") + 4)

            total_clusters = self.file_sys_manager.get_total_clusters()


            contador_entradas = 0 # contador para entradas livres encontradas

            i = 1 # Começa em 1 para pular a entrada reservada 0         
            # loop para ler todas as entradas FAT
            while i < total_clusters and contador_entradas < numero_entradas:

                # Lê 1 entrada (4 bytes)
                entrada_bytes = f.read(self.tamanho_entrada) 
                if len(entrada_bytes) != self.tamanho_entrada:
                    break  # fim real da FAT

                # Tranforma pra inteiro
                entrada_int = int.from_bytes(entrada_bytes, 'little')
                
                # Entrada livre, marcar
                if entrada_int == 0:                
                    entradas.append(i)  # Adiciona a posição da entrada livre à lista
                    contador_entradas += 1
                    
                # incrementa
                i+=1


        if len(entradas) < numero_entradas:
            __Error = "Não há entradas FAT livres suficientes."
            return entradas, __Error

        return entradas, None

    def alocar_entradas_FAT(self, tamanho_arquivo) :
        """
        Marca as entradas na FAT como ocupadas, criando uma cadeia (chain) onde cada 
        entrada aponta para o próximo cluster do arquivo.

        :param tamanho_arquivo: tamanho em bytes do arquivo a ser alocado.
        :return: Uma lista com os índices dos clusters alocados ou False em caso de erro.
        """
        endereco_particao = self.file_sys_manager.get_endereco_particao()
        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        quantidade_de_clusters = math.ceil(tamanho_arquivo/tamanho_cluster)
        
        entradas, __Error = self.buscar_entradas_livres(quantidade_de_clusters) 



        # separa a quantia de clusters livres necessários para o arquivo
       
        if __Error is not None: # se tem clusters livres 
            return False
    
        with open(endereco_particao, 'r+b') as f:
            
            # pega as entradas livres necessárias na tabela FAT

            for i in range(len(entradas)): # posiciona o cursor na posição absoluta da entrada FAT

                # Calcula a posição física somando o início da FAT com o índice do cluster * 4 bytes
                posicao = self.file_sys_manager.get_offset("fat1") + (entradas[i] * 4)  
                f.seek(posicao)

                if i == len(entradas)-1: # se for o final da chain marca como EOF
    
                    f.write(self.FAT_EOF.to_bytes(4, byteorder='little'))

                    break # sai do loop pois ja alocou todos os clusters necessários

                else: # se nao for o final da chain aponta para o próximo cluster
                    proximo_cluster = entradas[i + 1]
                    f.write(proximo_cluster.to_bytes(self.tamanho_entrada, 'little'))
                    
                        
        return entradas

    
    def desalocar_arquivo(self, primeiro_cluster):
        """
        Percorre a cadeia de clusters de um arquivo na FAT e marca todas as entradas como livres (0).

        :param primeiro_cluster: O índice do primeiro cluster do arquivo.
        :return: int: Retorna -1 após a conclusão.
        """
        endereco_particao = self.file_sys_manager.get_endereco_particao()

        livre = 0x00000000
        fim = 0xFFFFFFFF

        cluster_atual = primeiro_cluster
        with open(endereco_particao, 'r+b') as file:
            while True:
                posicao = self.file_sys_manager.get_offset("fat1") + (cluster_atual * 4) # Entrada de 4bytes
                file.seek(posicao) # posiciona o cursor na entrada

                proximo_cluster = int.from_bytes(file.read(4), 'little') # lê os bytes da posição para saber qual o próximo

                file.seek(posicao) # volta para a posicao do cluster para sobrescrevê-lo
                file.write(livre.to_bytes(4, 'little')) # redefine o cluster para livre (0)

                if proximo_cluster == fim: # cluster = EOF
                    break

                cluster_atual = proximo_cluster
        
        return -1

    def pegar_clusters_arquivo(self, primeiro_cluster):
        """
        Segue a cadeia de clusters na FAT a partir de um ponto inicial para reconstruir a lista de índices.

        :param primeiro_cluster: O índice inicial do arquivo.
        :return: list: Lista com as posições relativas (índices) dos clusters que compõem o arquivo.
        """

        visitados = set() # proteção contra loop infinito (corrupção de dados na FAT)
        endereco_particao = self.file_sys_manager.get_endereco_particao()
        
        cluster_chain = []
        cluster_atual = primeiro_cluster 


        # abre o storage na posicao do primeiro cluster:
        with open(endereco_particao, 'r+b') as f:

            while True: 
                
                if cluster_atual in visitados:
                    raise RuntimeError("Loop detectado na FAT")
                
                visitados.add(cluster_atual) # salva o caminho para verificação de loop
                cluster_chain.append(cluster_atual) # salva o cluster atual na lista de retorno

                posicao_fat = self.file_sys_manager.get_offset("fat1") + (cluster_atual * self.tamanho_entrada) # desloca o leitor ate a entrada atual
                f.seek(posicao_fat)

                entrada_bytes = f.read(self.tamanho_entrada) # le o conteudo da entrada (ponteiro para o próximo)

                proximo_cluster = int.from_bytes(entrada_bytes, 'little') 

                if proximo_cluster == 0x00000000: # testa se está vazio (erro de integridade)
                    return (f"[sys] Erro na leitura da cluster chain: cluster {cluster_atual} aponta para entrada livre")
            

                elif proximo_cluster == 0xFFFFFFFF: # se a entrada atual for a ultima (EOF), retorna a lista
                    return cluster_chain

                cluster_atual = proximo_cluster # continua a chain


    def sincronizar_fat_1_2(self):
        """
        Realiza a cópia idêntica da FAT1 para a FAT2 para manter a redundância do sistema.
        """
        endereco_particao = self.file_sys_manager.get_endereco_particao()
        bytesPorSetor = self.file_sys_manager.get_bytes_por_setor()
        setoresPorTabela = self.file_sys_manager.get_setores_por_tabela()
        size = bytesPorSetor * setoresPorTabela # calcula o tamanho da tabela fat em bytes

        with open(endereco_particao, 'r+b') as file:
            file.seek(self.file_sys_manager.get_offset("fat1"))
            dados = file.read(size) # copia os dados integrais da fat 1

            file.seek(self.file_sys_manager.get_offset("fat2")) 
            file.write(dados) # cola os dados na fat 2
        return