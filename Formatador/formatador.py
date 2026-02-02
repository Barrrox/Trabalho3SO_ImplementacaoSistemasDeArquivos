# contém as classes e processos necessários para formatar um armazenamento para FAT48

 # funções::
    # Zerar o armazenamento
    # Escrever o boot record

class Formatador:

    # tamanho partição em bytes
    def zerar(self, caminho_particao, tamanho_particao):
        # preenche a particao com 0s

        with open(caminho_particao, 'wb') as f:
            f.seek(tamanho_particao - 1)
            f.write(b'\x00')
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


    def formatar_completo(self, caminho_particao, tamanho_particao, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz):
        # formata o armazenamento completamente para FAT48
        # boot record | tabela FAT 1 | tabela FAT 2 | root dir | área de dados

        # Preenche com zeros
        self.zerar(caminho_particao, tamanho_particao) 
        
        # Escreve as inforamações no boot record
        self.escreve_boot_record(caminho_particao, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz)
        
        return    
