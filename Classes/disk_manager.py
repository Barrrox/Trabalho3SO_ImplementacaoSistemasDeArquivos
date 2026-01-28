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

        #endereco_particao = r"C:\Users\Usuario\Desktop\Unio\SO\TRAB3\Trabalho3SO_ImplementacaoSistemasDeArquivos\disco_virtual.bin"
        endereco_particao = self.file_sys_manager.get_endereco_particao()

        with open(endereco_particao, 'r+b') as f:
            f.seek(posicao)

            lido = f.read(self.tamanho_setor)  # lê 1 setor # talvez acessar uma variavel da classe a cada leitura cause lentidão, não sei
        
        return lido

    def escrever_setor(self, posicao, dados): 
        """
        Docstring for escrever_setor
        
        :param posicao: posicao de escrita no arquivo
        :param dados: dados a serem escritos, deve ter tamanho de 1 setor
        """

        #endereco_particao = r"C:\Users\Usuario\Desktop\Unio\SO\TRAB3\Trabalho3SO_ImplementacaoSistemasDeArquivos\disco_virtual.bin"
        endereco_particao = self.file_sys_manager.get_endereco_particao()

        with open(endereco_particao, 'r+b') as f:
            f.seek(posicao)   
            dados = f.write(dados)

            if f.tell() == int(posicao) + self.tamanho_setor: # se escreveu certo, posicao inicial + tamanho de um setor é a mesma da posição de término
                
                return dados  # retorna a quantia de bytes escritos para rodar o teste  

            else: # se não
                return False