# contém as classes e processos necessários para formatar um armazenamento para FAT48

 # funções::
    # Zerar o armazenamento
    # Escrever o boot record

class Formatador:

    def get_offset(self, secao):
        bytes_setor = self.file_sys_manager.get_bytes_por_setor()
        setores_por_tabela = self.file_sys_manager.get_setores_por_tabela()
        numero_entradas_raiz = self.file_sys_manager.get_num_entradas_raiz()
        tamanho_entrada = 22  # tamanho de cada entrada em bytes

        if secao == "boot_record":
            return 0
        
        elif secao == "fat1":
            return bytes_setor  # offset boot record
        
        # elif secao == "fat2":
        #     return bytes_setor + (setores_por_tabela * bytes_setor)  # offset boot record + tabela FAT 1
        elif secao == "root_dir":
            return bytes_setor + ( (setores_por_tabela * bytes_setor) * 2)  # offset boot record + 2 tabelas FAT
        
        elif secao == "area_dados":
            return (bytes_setor + ( (setores_por_tabela * bytes_setor) * 2) +
                    (numero_entradas_raiz * tamanho_entrada))  # offset root dir + tamanho root dir
        
        else:
            return None

    # tamanho partição em bytes
    def zerar(self, caminho_particao, tamanho_particao):
        # preenche a particao com 0s
        
        # opção 1
        with open(caminho_particao, 'wb') as f:
            f.write(b'\x00' * tamanho_particao)

        # # opção 2
        # with open(caminho_particao, 'wb') as f:
        #     f.seek(tamanho_particao - 1)
        #     f.write(b'\x00')
        

        return 

    # recebe os parametros em valor numérico, faz a tradução para binário (little-endian) na hora da escrita
    def escreve_boot_record(self, arquivo, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz):

        # escreve os parâmetros do boot record
        with open(arquivo, 'r+b') as f:

            f.seek(3)  # Pular os primeiros 3 bytes reservados
            f.write(bytes_por_setor.to_bytes(2, byteorder='little'))       # 2 bytes

            f.seek(5)  # Pular para o offset 5
            f.write(setores_por_tabela.to_bytes(4, byteorder='little'))    # 4 bytes

            f.seek(9)  # Pular para o offset 9
            f.write(setores_por_cluster.to_bytes(1, byteorder='little'))   # 1 byte

            f.seek(10) # Pular para o offset 10
            f.write(num_entradas_raiz.to_bytes(2, byteorder='little'))     # 2 bytes

        return  
        # def escreve_boot_record(self, arquivo, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz ):

    #     # escreve os parâmetros do boot record
    #     with open(arquivo, 'r+b') as f:

    #         f.seek(3)  # Pular os primeiros 3 bytes reservados
    #         f.write(bytes_por_setor.to_bytes(2, byteorder='little'))       # 2 bytes

    #         f.seek(5)  # Pular para o offset 5
    #         f.write(setores_por_tabela.to_bytes(4, byteorder='little'))    # 4 bytes

    #         f.seek(9)  # Pular para o offset 9
    #         f.write(setores_por_cluster.to_bytes(1, byteorder='little'))   # 1 byte

    #         f.seek(10) # Pular para o offset 10
    #         f.write(num_entradas_raiz.to_bytes(2, byteorder='little'))     # 2 bytes

    #     return  
    
    def escreveFATs(self, arquivo):
        # escreve as tabelas FAT
        setor = self.file_sys_manager.get_bytes_por_setor()
        setores_por_tabela = self.file_sys_manager.get_setores_por_tabela()
        offset_fat1 = self.get_offset("fat1")
        with open(arquivo, 'r+b') as f:
            
            f.seek(offset_fat1)  # Pular para o início da primeira tabela FAT
            
            # escreve as tabelas FAT
            for i in range(setores_por_tabela * setor * 2): 
                 # setores por tabela * tamanho do setor * 2 tabelas FAT = total de bytes (entradas) a serem alocados
                f.write(b'\x00')  # Preencher a tabela FAT com zeros

        return
    
    def escreveRootDir(self, arquivo):
        # escreve o root dir
        numero_entradas = self.file_sys_manager.get_num_entradas_raiz()
        tamanho_entrada = 22  # tamanho de cada entrada em bytes
        
        offset_root_dir = self.get_offset("root_dir")
                           

        with open(arquivo, 'r+b') as f:
            f.seek(offset_root_dir)  # Pular para o início do root dir
            
            for i in range(numero_entradas * tamanho_entrada):
                f.write(b'\x00')  # Preencher o root dir com zeros

        return
    
    def alocaAreaDeDados(self, arquivo):
        # aloca a area de dados
        
        offset_area_dados = self.get_offset("area_dados")

        with open(arquivo, 'r+b') as f:
            f.seek(offset_area_dados)  # Pular para o início da área de dados
        
        i = True
        posicao_lida = 0
        
        while i != EOFError: # como o tamanho do arquivo é desconhecido, lê até o final e vai gravando
            f.seek(offset_area_dados + posicao_lida)
            i = f.tell()
            if i:
                f.write(b'\x00')  # Preencher a área de dados com zeros
                posicao_lida += 1
        
        return

    def formatar_completo(self, caminho_particao, tamanho_particao, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz):
        # formata o armazenamento completamente para FAT48
        # boot record | tabela FAT 1 | tabela FAT 2 | root dir | área de dados

        # Preenche com zeros
        self.zerar(caminho_particao, tamanho_particao) 
        
        # Escreve as inforamações no boot record
        self.escreve_boot_record(caminho_particao, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz)
        
        return    
