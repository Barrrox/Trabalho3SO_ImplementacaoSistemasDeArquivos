import math

class FAT_table_manager:

    def __init__(self, file_sys_manager):
        self.file_sys_manager = file_sys_manager
        self.data_manager = file_sys_manager.data_manager
        self.root_manager = file_sys_manager.root_dir_manager

    def procurar_entradas_FAT(self, arquivo, numero_entradas): # pega a posição relativa de uma entrada FAT livre
        """
        Procura 'numero_entradas' entradas livres no arquivo

        Parâmetros:
            arquivo: path absoluto para o arquivo
            numero_entradas: número de entradas requeridas

        Retorna:
            entradas: lista com as posiçõe relativas das entradas livres encontradas 
            
        """
        
        offset_fat = self.file_sys_manager.get_offset("fat1")
        
        entradas = []
        with open(arquivo, 'r+b') as f:
            f.seek(offset_fat)

            posicao = 0
         
            # loop começando em 1 para ignorar a entrada 0 (reservada)        
            for i in range(1, numero_entradas+1):
                f.seek(posicao)
                entrada_bytes = f.read(4)  # Lê 4 bytes (32 bits) da entrada FAT
                
                # Se entrada ocupada
                if entrada_bytes != 0x00000000:                   
                    
                    pass # Entrada ocupada, continua procurando
                else:
                    entradas.append(i)  # Adiciona a posição da entrada livre à lista

        if len(entradas) < numero_entradas:
            __Error = "Não há entradas FAT livres suficientes."
            return entradas, __Error

        return entradas, None

    def alocar_arquivo(self, tamanho_arquivo, arquivo):

        # falta alterar o campo 1° cluster da entrada do arquivo no root dir

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()

        quantidade_de_clusters = math.ceil(tamanho_arquivo/tamanho_cluster)

        # separa a quantia de clusters livres necessários para o arquivo
        clusters_alocados, __Error = self.procurar_clusters_livre(quantidade_de_clusters)
       
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
    
    def procurar_clusters_livre(self, n_clusters):
        offset_fat = self.file_sys_manager.get_offset("fat")
        clusters_livres = []
        total_de_clusters_no_disco = self.file_sys_manager
        
        with open(self.file_sys_manager.endereco_particao, 'rb') as f:
            f.seek(offset_fat)
            # Varre as entradas da FAT
            # O índice da entrada é o número do cluster
            for i in range(total_de_clusters_no_disco):
                entrada = int.from_bytes(f.read(4), 'little')
                if entrada == 0x00000000:
                    clusters_livres.append(i)
                
                if len(clusters_livres) == n_clusters:
                    break
        return clusters_livres

    
    def desalocar_arquivo(primeiro_cluster):
        # desaloca os clusters de um arquivo alocado na tabela
        return

    def pegar_proximo_cluster():
        # Encontra o proximo cluster de uma chain     
        return

    def sincronizar_fat(primeiro_cluster):
        # Sincroniza as tabelas FAT
        return
    
