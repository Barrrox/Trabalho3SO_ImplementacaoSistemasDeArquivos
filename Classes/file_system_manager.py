class FileSystemManager:
    
    def __init__(self):
    # Inicializa os atributos do Boot Record
    # self._<atributo> representa um atributo PRIVATE  
        self.__bytes_por_setor     = 512                        # 2 bytes # ALTERAR PARA FSEEK DE ARQUIVO DPS, HARDCODE SO PARA TESTE
        self.__setores_por_tabela  = 131072                  # 4 bytes
        self.__setores_por_cluster = 8                      # 1 byte
        self.__num_entradas_raiz   = 512                 # 2 bytes

    def get_bytes_por_setor(self):
        """
        retorna o número de bytes por setor
        """

        return self.__bytes_por_setor
    

    def get_setores_por_tabela(self):
        """
        retorna o número de setores por tabela
        """
        return self.__setores_por_tabela
    

    def get_setores_por_cluster(self):
        """
        retorna o número de setores por cluster
        """
        return self.__setores_por_cluster
        

    def get_num_entradas_raiz(self):
        """
        retorna o número de entradas do root dir
        """
        return self.__num_entradas_raiz
    
  