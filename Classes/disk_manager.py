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
 
    def ler_setor(self, posicao, f):
        """
        Realiza a leitura de um único setor no endereço especificado.
        
        :param posicao: int: Endereço absoluto em bytes para o início da leitura.
        :param f: ponteiro para o arquivo (para usar f.seek, f.read, etc)
        :return: bytes: Conteúdo binário lido do setor.

        """

        f.seek(posicao)
        lido = f.read(self.file_sys_manager.get_bytes_por_setor())
        
        return lido

    def escrever_setor(self, posicao, dados, f): 
        """
        Grava uma sequência de bytes num setor específico.
        
        :param posicao: int: Endereço absoluto em bytes para o início da escrita.
        :param dados: bytes: Dados a serem gravados (deve ter o tamanho exato de um setor).
        :param f: ponteiro para o arquivo (para usar f.seek, f.read, etc)
        :return: int ou bool: Quantidade de bytes escritos ou False se houver falha de integridade.
        """
                
        f.seek(posicao)   
        dados_escritos = f.write(dados)
        
        # Validação: verifica se a posição atual do ponteiro após a escrita 
        # corresponde à posição inicial somada ao tamanho do setor esperado.
        if f.tell() == int(posicao) + self.file_sys_manager.get_bytes_por_setor():
            return dados_escritos
        else:
            return False