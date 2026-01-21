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

        escritas = math.ceil(len(dados) / self.tamanho_setor)
        bytes_escritos = 0
        with open(arquivo, 'r+b') as f:
            f.seek(posicao)

            for i in range(escritas):
                f.write(dados)
                bytes_escritos += len(dados)

            if bytes_escritos != len(dados):
                print(f"Erro na escrita do setor. bytes_escritos != len(dados): {bytes_escritos} != {len(dados)}")
            if bytes_escritos + len(dados) != f.tell():
                print(f"Erro na escrita do setor. bytes_escritos + len(dados) != f.tell(): {bytes_escritos} + {len(dados)} != {f.tell()}")

        return bytes_escritos