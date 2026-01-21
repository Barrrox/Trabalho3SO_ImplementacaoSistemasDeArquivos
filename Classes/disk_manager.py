from Classes.file_system_manager import FileSystemManager
import math

class  disk_manager:
    def __init__(self):
        self.file_sys_manager = FileSystemManager()

        tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        setores_por_cluster = self.file_sys_manager.get_setores_por_cluster()

        cluster_em_bytes = setores_por_cluster * tamanho_setor

    # posicao == posição absoluta em bytes no arquivo
    # dados == tamanho em clusters do conjunto de dados a ser lido naquela posição
    # retorna uma lista com os dados lidos, cada posição da lista é 1 setor (512 bytes)
    def ler_setor(self, arquivo, posicao, dados):

        dados *= self.cluster_em_bytes
        leituras = math.ceil(dados / self.tamanho_setor)

        lido = []

        with open(arquivo, 'r+b') as f:
            f.seek(posicao)

            for i in range(leituras):
                lido.append(f.read(self.tamanho_setor))  # lê 512 bytes (1 setor) # talvez acessar uma variavel da classe a cada leitura cause lentidão, não sei
        
        return lido


    # posicao == posição absoluta em bytes no arquivo
    # dados == conjunto de dados completo a serem escritos naquela posição
    def escrever_setor(self, arquivo, posicao, dados): 

        escritas = math.ceil(len(dados) / self.tamanho_setor) # quantia de setores a serem escritos
        bytes_escritos = 0
        with open(arquivo, 'r+b') as f:
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
                print(f"Erro na escrita do setor. bytes_escritos != len(dados): {bytes_escritos} != {len(dados)}")
            if bytes_escritos + len(dados) != f.tell():
                print(f"Erro na escrita do setor. bytes_escritos + len(dados) != f.tell(): {bytes_escritos} + {len(dados)} != {f.tell()}")

        return bytes_escritos