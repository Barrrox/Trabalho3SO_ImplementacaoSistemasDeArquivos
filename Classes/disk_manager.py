import math

class disk_manager:
    """
    Gerencia o acesso direto ao ficheiro da partição (disco virtual),
    realizando operações de leitura e escrita ao nível de setor.
    """
    
    def __init__(self, file_sys_manager):
        """
        Inicializa o gerenciador de disco com os parâmetros físicos da partição.
        
        :param file_sys_manager: Instância do FileSystemManager para acesso a configurações.
        """
        self.file_sys_manager = file_sys_manager

        self.tamanho_setor = self.file_sys_manager.get_bytes_por_setor()
        self.tamanho_cluster = self.file_sys_manager.get_tamanho_cluster()
        self.setores_por_cluster = self.file_sys_manager.get_setores_por_cluster()

        self.cluster_em_bytes = self.setores_por_cluster * self.tamanho_setor
 
    def ler_setor(self, posicao):
        """
        Realiza a leitura de um único setor no endereço especificado.
        
        :param posicao: int: Endereço absoluto em bytes para o início da leitura.
        :return: bytes: Conteúdo binário lido do setor.
        """

        endereco_particao = self.file_sys_manager.get_endereco_particao()

        with open(endereco_particao, 'r+b') as f:
            f.seek(posicao)
            lido = f.read(self.tamanho_setor)
        
        return lido

    def escrever_setor(self, posicao, dados): 
        """
        Grava uma sequência de bytes num setor específico.
        
        :param posicao: int: Endereço absoluto em bytes para o início da escrita.
        :param dados: bytes: Dados a serem gravados (deve ter o tamanho exato de um setor).
        :return: int ou bool: Quantidade de bytes escritos ou False se houver falha de integridade.
        """

        endereco_particao = self.file_sys_manager.get_endereco_particao()
        
        with open(endereco_particao, 'r+b') as f:
            f.seek(posicao)   
            dados_escritos = f.write(dados)
            
            # Validação: verifica se a posição atual do ponteiro após a escrita 
            # corresponde à posição inicial somada ao tamanho do setor esperado.
            if f.tell() == int(posicao) + self.tamanho_setor:
                return dados_escritos
            else:
                return False