from Classes.FAT_table_manager import FAT_table_manager
from Classes.disk_manager import disk_manager
from Classes.root_dir_manager import root_dir_manager
from Classes.data_manager import data_manager

class FileSystemManager:
    
    def __init__(self):
    # Inicializa os atributos do Boot Record
    # self._<atributo> representa um atributo PRIVATE  
        self.__bytes_por_setor     = 512                        # 2 bytes # ALTERAR PARA FSEEK DE ARQUIVO DPS, HARDCODE SO PARA TESTE
        self.__setores_por_tabela  = 131072                  # 4 bytes
        self.__setores_por_cluster = 8                      # 1 byte
        self.__num_entradas_raiz   = 512                 # 2 bytes
        self.fat_manager = FAT_table_manager()
        self.root_manager = root_dir_manager()
        self.data_manager = data_manager()
        self.disk_manager = disk_manager()
        
#*******************************************************************************************************#
    def get_bytes_por_setor(self):
        """
        retorna o número de bytes por setor
        """

        return self.__bytes_por_setor
#*******************************************************************************************************#
    def get_setores_por_tabela(self):
        """
        retorna o número de setores por tabela
        """
        return self.__setores_por_tabela
#*******************************************************************************************************#
    def get_setores_por_cluster(self):
        """
        retorna o número de setores por cluster
        """
        return self.__setores_por_cluster 
#*******************************************************************************************************#
    def get_num_entradas_raiz(self):
        """
        retorna o número de entradas do root dir
        """
        return self.__num_entradas_raiz
#*******************************************************************************************************#    
    def ler_input_interface(self, input_string):
        """
        Lê o input da interface do usuário
   
        1. verifica se a string é um comando válido
        2. caso válido, envia a string para o método disparar_comando
        3. caso inválido, retorna mensagem de comando incorreto
        """

        # strings_unitarias é um vetor das seções presentes na input string
        strings_unitarias = input_string.split()

        if not strings_unitarias:
            return ("Comando inválido ou não existente! -1")
        else:
            return self.disparar_comando(strings_unitarias)    
#*******************************************************************************************************# 
    def disparar_comando(self, stringComando):
        """
        Dispara o comando recebido com argumentos
        """
        
        comando = stringComando[0]
        argumentos = stringComando[1:]

        # Essa seção verifica se o comando existe como método dentro da classe, tais estão nomeados como "comando_<nome_do_comando>"
        # def comando_<oq o cara digitou no terminal>(self, <*args se forem usar argumentos>):
        # acessar individualmente cada casa da tupla para ter acesso ao argumento
        
        comando_requerido = f"comando_{comando}"
        if hasattr(self, comando_requerido):
            metodo = getattr(self, comando_requerido)
            return metodo(*argumentos)
        else:
            return ("Comando inválido ou não existente! -2")            
#*******************************************************************************************************#
    def comando_exemplo(self, *args):

        return f"Comando de exemplo! você escreveu 'exemplo' seguido de {args}."
#*******************************************************************************************************#
    # Exemplo de comando usando retorno com dicionarios
    def comando_exemplo2(self, argumento_teste):

        if argumento_teste == 1:
            return {"rodou?": True, "comando" : "exemplo2", "dados" : 1, "msg_erro": None}
        else:
            return {"rodou?": False, "comando" : "exemplo2", "dados" : None, "msg_erro": "Não digitou 1"}

#*******************************************************************************************************#   
    def comando_deletar_arqv(self, *args):
        arquivo = args[2].lower()
        
        if not arquivo:
            erro = ["Erro: arquivo não encontrado"]
            return erro

        resultado = [f"arquivo {arquivo} excluido"]

        return resultado
#*******************************************************************************************************#
    def comando_bootrecord(self):

        bytes_por_setor = self.get_bytes_por_setor()
        setores_por_tabela = self.get_setores_por_tabela()
        setores_por_cluster = self.get_setores_por_cluster()
        num_entradas_raiz = self.get_num_entradas_raiz()

        bootrecord = [f"Informações do boot record:",
                      f"Bytes por setor: {bytes_por_setor}",
                      f"Setores por tabela: {setores_por_tabela}",
                      f"Setores por cluster: {setores_por_cluster}",
                      f"Número de entradas no diretório raiz: {num_entradas_raiz}"
                      ]
        return bootrecord
#*******************************************************************************************************#
    
    def comando_copiar(self): # copia os elementos
        return

    def comando_listar(self): # lista os elementos do diretório
        return

    def comando_mover(self): # move elemento de um diretório para outro
        return





    
  