import math

class disk_manager:
    
    def __init__(self, file_sys_manager):
        self.file_sys_manager = file_sys_manager

        self.tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        self.tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        self.setores_por_cluster = self.file_sys_manager.get_setores_por_cluster()

        self.cluster_em_bytes = self.setores_por_cluster * self.tamanho_setor
 
    def ler_setor(self, posicao):
        """
        Docstring for ler_setor
        
        :param posicao: Posição para iniciar a leitura do setor
        :return: string com os dados lidos
        """

        endereco_particao = self.file_sys_manager.get_endereco_particao()

        with open(endereco_particao, 'r+b') as f:
            f.seek(posicao)

            lido = f.read(self.tamanho_setor)  # lê 1 setor # talvez acessar uma variavel da classe a cada leitura cause lentidão, não sei
        
        return lido


    # posicao == posição absoluta em bytes no arquivo
    # dados == conjunto de dados completo a serem escritos naquela posição
    def escrever_setor(self, posicao, dados): 

        endereco_particao = self.file_sys_manager.get_endereco_particao()

        escritas = math.ceil(len(dados) / self.tamanho_setor) # quantia de setores a serem escritos
        bytes_escritos = 0
        with open(endereco_particao, 'r+b') as f:
            f.seek(posicao)

            for i in range(escritas):

                inicio_escrita = i * self.tamanho_setor
                fim_escrita = inicio_escrita + self.tamanho_setor

                setor_a_escrever = dados[inicio_escrita:fim_escrita] # pega 1 setor dos byte_array dos dados para escrever

                if len(setor_a_escrever) < self.tamanho_setor:
                    # se o setor a escrever for menor que o tamanho do setor, completa com zeros
                    setor_a_escrever += b'\x00' * (self.tamanho_setor - len(setor_a_escrever))

                f.write(setor_a_escrever)
                bytes_escritos += len(setor_a_escrever)

            if bytes_escritos != len(dados):
                return (f"Erro na escrita do setor. bytes_escritos != len(dados): {bytes_escritos} != {len(dados)}")
            if bytes_escritos + len(dados) != f.tell():
                return (f"Erro na escrita do setor. bytes_escritos + len(dados) != f.tell(): {bytes_escritos} + {len(dados)} != {f.tell()}")

        return bytes_escritos