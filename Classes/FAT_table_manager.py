import math

class FAT_table_manager:

    def __init__(self, file_sys_manager):
        self.file_sys_manager = file_sys_manager
        self.data_manager = file_sys_manager.data_manager
        self.root_manager = file_sys_manager.root_dir_manager


    def verificar_espaco_disponivel(self, tamanho_arquivo):      
        
        """
        Verifica se há espaço disponível na tabela FAT para alocar um arquivo de tamanho 'tamanho_arquivo'

        Parâmetros:
            tamanho_arquivo: tamanho do arquivo a ser alocado

        Retorna:
            bool: True se houver espaço disponível, False caso contrário
            
        """

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        quantidade_de_clusters_necessarios = math.ceil(tamanho_arquivo / tamanho_cluster)
        
        entradas = self.buscar_entradas_livres(quantidade_de_clusters_necessarios)

        if len(entradas) != quantidade_de_clusters_necessarios:
            return False

        else:   
            return True

    def buscar_entradas_livres(self, numero_entradas): # pega a posição relativa de uma entrada FAT livre
        """
        Procura entradas livres na partição e retorna suas posições relativas

        Parâmetros:
            numero_entradas: número de entradas requeridas

        Retorna:
            entradas: lista com as posições relativas das entradas livres encontradas 
            
        """

        endereco_particao = self.file_sys_manager.get_endereco_particao()
        
        offset_fat = self.file_sys_manager.get_offset("fat1")
        
        entradas = []
        with open(endereco_particao, 'rb') as f:
            
            # Começa da entrada 1, ignorando a entrada reservada 0
            f.seek(offset_fat + 4)

            total_clusters = self.file_sys_manager.get_total_clusters()


            contador_entradas = 0 # contador para entradas livres encontradas
            i = 1 # Começa em 1 para pular a entrada reservada 0         
            # loop para ler todas as entradas FAT
            while i < total_clusters and contador_entradas < numero_entradas:

                # Lê 1 entrada (4 bytes)
                entrada_bytes = f.read(4) 

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
        tamanho_arquivo: tamanho em bytes do arquivo a ser alocado
        
        """
        endereco_particao = self.file_sys_manager.get_endereco_particao()

        # falta alterar o campo 1° cluster da entrada do arquivo no root dir

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()

        quantidade_de_clusters = math.ceil(tamanho_arquivo/tamanho_cluster)

        entradas, __Error = self.buscar_entradas_livres(quantidade_de_clusters) 

        offset_fat = self.file_sys_manager.get_offset("fat1")

        # separa a quantia de clusters livres necessários para o arquivo
       
        if __Error == None: # se tem clusters livres 
    
            with open(endereco_particao, 'r+b') as f:
                
                # pega as entradas livres necessárias na tabela FAT

                for i in range(len(entradas)): # posiciona o cursor na posição absoluta da entrada FAT

                    posicao = offset_fat + (entradas[i] * 4)  # Cada entrada FAT tem 4 bytes
                    posicao = posicao.to_bytes(4, byteorder='little')
                    f.seek(posicao)

                    if i == len(entradas)-1: # se for o final da chain marca como EOF
                        final_cluster_chain = 0xFFFFFFFF  # EOF relativo ao sistema de arquivos, já em binário
                        f.write(final_cluster_chain)

                        break # sai do loop pois ja alocou todos os clusters necessários

                    else: # se nao for o final da chain aponta para o próximo cluster
                        posicao_prox_cluster = offset_fat + (entradas[i+1] * 4)
                        posicao_prox_cluster = posicao_prox_cluster.to_bytes(4, byteorder='little')
                        
                        f.write(posicao_prox_cluster)
        else:
            return False
                        
        return entradas

    
    def desalocar_arquivo(self, primeiro_cluster):
        # desaloca os clusters de um arquivo alocado na tabela
        endereco_particao = self.file_sys_manager.get_endereco_particao()
        offset_fat = self.file_sys_manager.get_offset("fat1")

        livre = 0x00000000
        fim = 0xFFFFFFFF

        cluster_atual = primeiro_cluster
        with open(endereco_particao, 'r+b') as file:
            while True:
                posicao = offset_fat + (cluster_atual * 4) # Entrada de 4bytes
                file.seek(posicao) # posiciona o cursor na entrada

                proximo_cluster = int.from_bytes(file.read(4), 'little') # lê os bytes da posição (littlend) e transforma pra inteiro

                file.seek(posicao) # volta para a posicao do cluster
                file.write(livre.to_bytes(4, 'little')) # redefine o cluster para livre

                if proximo_cluster == fim: # cluster = EOF
                    break

                cluster_atual = proximo_cluster
        
        return -1

    def pegar_clusters_arquivo(self, primeiro_cluster):
        # Encontra todos os clusters de um arquivo
        # Retorna: lista com as posições absolutas dos clusters desse arquivo 
        # ex : lista = [0x02374033, 0x129347698]

        endereco_particao = self.file_sys_manager.get_endereco_particao()
        
        cluster_chain = [primeiro_cluster]

        # abre o storage na posicao do primeiro cluster:
        with open(endereco_particao, 'r+b') as f:
            posicao_atual = f.seek(primeiro_cluster)
            entrada = f.read(4)

            while True: # 

                entrada = f.read(4)

                if entrada != 0xFFFFFFFF and int(entrada) != 0: # se a entrada na FAT nao eh o final do arquivo e nem vazia -> sinaliza o proximo cluster da chain

                    cluster_chain.append(bin(entrada)) # salva o endereço do proximo cluster na lista de retorno

                    posicao_atual = bin(entrada) # salta para o proximo cluster
                    f.seek(posicao_atual)

                elif entrada == 0xFFFFFFFF: # se a entrada atual for a ultima
                    return cluster_chain

                else: # se nao caiu em nenhum eh pq tava vazia por algum motivo
                    error = f"[sys] - Erro na leitura da cluster chain, {cluster_chain[-1]} apontou para uma entrada vazia"
                    return error 

        return -1


    def sincronizar_fat_1_2(self):
        # Sincroniza as tabelas FAT
        endereco_particao = self.file_sys_manager.get_endereco_particao()

        offset_fat1 = self.file_sys_manager.get_offset("fat1")
        offset_fat2 = self.file_sys_manager.get_offset("fat2")
        bytesPorSetor = self.file_sys_manager.get_bytes_por_setor()
        setoresPorTabela = self.file_sys_manager.get_setores_por_tabela()
        size = bytesPorSetor * setoresPorTabela # calcula o tamanho da tabela fat

        with open(endereco_particao, 'r+b') as file:
            file.seek(offset_fat1)
            dados = file.read(size) # copia os dados da fat 1

            file.seek(offset_fat2) 
            file.write(dados) # cola os dados na fat 2
        return