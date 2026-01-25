import math

class FAT_table_manager:

    def __init__(self, file_sys_manager):
        self.file_sys_manager = file_sys_manager
        self.data_manager = file_sys_manager.data_manager
        self.root_manager = file_sys_manager.root_dir_manager


    def verificar_espaco_disponivel(self, arquivo, tamanho_arquivo):      
        
        """
        Verifica se há espaço disponível na tabela FAT para alocar um arquivo de tamanho 'tamanho_arquivo'

        Parâmetros:
            arquivo: path absoluto para o arquivo
            tamanho_arquivo: tamanho do arquivo a ser alocado

        Retorna:
            bool: True se houver espaço disponível, False caso contrário
            
        """
        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        quantidade_de_clusters_necessarios = math.ceil(tamanho_arquivo / tamanho_cluster)
        
        entradas = self.procurar_entradas_FAT(arquivo, quantidade_de_clusters_necessarios)

        if len(entradas) != quantidade_de_clusters_necessarios:
            return False

        else:   
            return True

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

    def alocar_entradas_FAT(self, sistema, tamanho_arquivo) :
        """
        sistema: path absoluto para o sistema de arquivos
        tamanho_arquivo: tamanho do arquivo a ser alocado
        
        """

        # falta alterar o campo 1° cluster da entrada do arquivo no root dir

        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()

        quantidade_de_clusters = math.ceil(tamanho_arquivo/tamanho_cluster)

        entradas, __Error = self.procurar_entradas_FAT(sistema, quantidade_de_clusters) 

        offset_fat = self.file_sys_manager.get_offset("fat1")

        # separa a quantia de clusters livres necessários para o arquivo
       
        if __Error == None: # se tem clusters livres 
    
            with open(sistema, 'r+b') as f:
                
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
            return print("Não há clusters livres suficientes para alocar o arquivo.")
                        
        return entradas

    
    def desalocar_arquivo(primeiro_cluster):
        # desaloca os clusters de um arquivo alocado na tabela
        return

    def pegar_proximo_cluster():
        # Encontra o proximo cluster de uma chain     
        return

    def sincronizar_fat_1_2(primeiro_cluster):
        # Sincroniza as tabelas FAT
        return