from math import ceil
from os import path

from Classes.FAT_table_manager import FAT_table_manager
from Classes.disk_manager import disk_manager
from Classes.root_dir_manager import root_dir_manager
from Classes.data_manager import data_manager
from Formatador.formatador import Formatador

class FileSystemManager:
    
    def __init__(self):
    # Inicializa os atributos do Boot Record
    # self._<atributo> representa um atributo PRIVATE  
        self.__bytes_por_setor     = 512    # 2 bytes
        self.__setores_por_tabela  = 131072 # 4 bytes
        self.__setores_por_cluster = 8      # 1 byte
        self.__num_entradas_raiz   = 512    # 2 bytes
        self.__endereco_particao = None
        self.__tamanho_total_particao = 0
  
        
        # Inicializa os managers que não tem dependências primeiro
        self.root_dir_manager = root_dir_manager(self)
        self.disk_manager = disk_manager(self)
        
        # Inicializa os managers que dependem dos anteriores
        self.data_manager = data_manager(self)
        self.fat_manager = FAT_table_manager(self)
      
#*******************************************************************************************************#
    def get_bytes_por_setor(self):
        """
        retorna o número de bytes por setor
        """

        return self.__bytes_por_setor
#*******************************************************************************************************#
    def set_bytes_por_setor(self, bytes_por_setor):
        """
        retorna o número de bytes por setor
        """

        self.__bytes_por_setor = bytes_por_setor

        return    
#*******************************************************************************************************#
    def get_setores_por_tabela(self):
        return self.__setores_por_tabela
#*******************************************************************************************************#
    def set_setores_por_tabela(self, setores_por_tabela):
        self.__setores_por_tabela = setores_por_tabela
        return
#*******************************************************************************************************#
    def get_setores_por_cluster(self):
        return self.__setores_por_cluster 
#*******************************************************************************************************#
    def set_setores_por_cluster(self, setores_por_cluster):
        self.__setores_por_cluster = setores_por_cluster
        return
#*******************************************************************************************************#
    def get_num_entradas_raiz(self):
        """
        retorna o número de entradas do root dir
        """
        return self.__num_entradas_raiz
#*******************************************************************************************************#
    def set_num_entradas_raiz(self, num_entradas_raiz):
        self.__num_entradas_raiz = num_entradas_raiz
        return
#*******************************************************************************************************#    
    def get_endereco_particao(self):
        """Retorna o caminho do arquivo .bin atual"""
        return self.__endereco_particao
#*******************************************************************************************************#    
    def set_endereco_particao(self, endereco):
        """
        Define o endereço da partição. 
        Valida se o caminho é uma string e se o arquivo realmente existe.
        """
        if isinstance(endereco, str):
            self.__endereco_particao = endereco
            return True
        return False
#*******************************************************************************************************#    
    def get_tamanho_total_particao(self):
        """Retorna o tamanho total da particao em bytes"""
        return self.__tamanho_total_particao
#*******************************************************************************************************#    
    def set_tamanho_total_particao(self, tamanho):
        """
        Define o tamanho total da partição em bytes
        Garante que o tamanho seja um valor numérico positivo.
        """
        if isinstance(tamanho, (int, float)) and tamanho >= 0:
            self.__tamanho_total_particao = tamanho
        return
        
#*******************************************************************************************************#    
    def get_offset(self, secao):
        """
        Retorna o offset (inteiro) em bytes de uma seção do BootRecord. O parâmetro seção pode deve ser
        uma das seguintes strings: "boot_record", "fat1", "fat2", "root_dir", "area_dados"
        """
        bytes_setor = self.get_bytes_por_setor()
        setores_por_tabela = self.get_setores_por_tabela()
        numero_entradas_raiz = self.get_num_entradas_raiz()
        tamanho_entrada = 22  # tamanho de cada entrada em bytes

        if secao == "boot_record":
            return 0
        
        elif secao == "fat":
            return bytes_setor  # offset boot record
        
        elif secao == "fat2":
            return bytes_setor + (setores_por_tabela * bytes_setor)  # offset boot record + tabela FAT 1
        
        elif secao == "root_dir":
            return bytes_setor + ( (setores_por_tabela * bytes_setor) * 2)  # offset boot record + 2 tabelas FAT
        
        elif secao == "area_dados":
            return (bytes_setor + ( (setores_por_tabela * bytes_setor) * 2) +
                    (numero_entradas_raiz * tamanho_entrada))  # offset root dir + tamanho root dir
        
        else:
            return None

#*******************************************************************************************************#
    def get_tamanho_cluster(self):
        """
        retorna o tamanho em bytes de 1 cluster na configuração atual
        """

        tamanho_setor = self.get_bytes_por_setor()
        setores_por_cluster = self.get_setores_por_cluster()

        tamanho_cluster = tamanho_setor*setores_por_cluster
        
        return tamanho_cluster
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
            erro = ["Comando inválido ou não existente!"]
            return erro
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
            erro = ["Comando inválido ou não existente!"]
            return erro
#*******************************************************************************************************#
    def comando_exemplo(self, *args):
        resultado = [f"Comando de exemplo! você escreveu 'exemplo' seguido de {args}."]
        return resultado
#*******************************************************************************************************#
    # Exemplo de comando usando retorno com dicionarios
    def comando_exemplo2(self, *args):

        if args[0] == 1:
            return {"rodou?": True, "comando" : "exemplo2", "dados" : 1, "msg_erro": None}
        else:
            return {"rodou?": False, "comando" : "exemplo2", "dados" : None, "msg_erro": "Não digitou 1"}

#*******************************************************************************************************#   
    # deletar nome_arqv
    def comando_deletar(self, *args):
        arquivo = args[0].lower()
        erro = ["[sys] - Arquivo não encontrado"]

        if not arquivo:
            return erro
        
        entrada = self.root_manager.ler_entrada(arquivo) # procura entrada do arquivo

        if not entrada:
            return erro

        # entrada = [atributo, nome, extensao, tamanho, dono, nivel_de_acesso, primeiro_cluster]
        primeiro_cluster = entrada[6]

        self.fat_manager.desalocar_arquivo(primeiro_cluster)
        self.root_manager.desalocar_entrada(arquivo)
        self.fat_manager.sincronizar_fat(primeiro_cluster)

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
    
    def comando_copiar(self, *args): # copia os elementos
        # comando_copiar diretorio1 diretorio2
        origem = args[1].lower()
        destino = args[2].lower()

        if not origem or not destino:
            erro = ["[sys] - É necessário informar a origem e o destino do arquivo"]
            return erro
        
        entrada_origem = self.root_manager.ler_entrada()
        if not entrada_origem:
            erro = ["[sys] - Arquivo não encontrado"]
            return erro

        # entrada = [atributo, nome, extensao, tamanho, dono, nivel_de_acesso, primeiro_cluster]
        # primeiro_cluster = self.fat_manager.alocar_arquivo(entrada_origem[3])

        return

    def comando_listar(self): # lista os elementos do diretório
        entradas = self.root_manager.listar_entradas()

        if not entradas:
            erro = ["[sys] - Diretório vazio"]
            return erro
        
        resultado = []
        for entrada in entradas:
            resultado.append(f"{entrada[0]}.{entrada[1]}")
        
        return resultado

    def comando_mover(self, *args): # move elemento de um diretório para outro

        # 1. Verificar se origem eh um arquivo existente
        # 2. Verificar se destino eh um diretorio existente
        # 3. Verificar se há espaço suficiente 
        #    Isso serve para a situação em que a particao está toda ocupada. Se está todo ocupado
        #    não será possível criar a cópia para mover antes de desalocar da origem. 
        # 4. Ler entrada
        buffer_entrada = self.root_dir_manager.ler_entrada()        
        # 5. Desalocar entrada antiga
        



        return
    
    def comando_formatar(self, *args):
        # Inicialização de variáveis via argumentos
        endereco_particao    = args[0]
        bytes_por_setor     = int(args[1])
        setores_por_cluster = int(args[2])
        num_entradas_raiz   = int(args[3])

        # Verificar se caminho válido
        if not path.exists(endereco_particao):
            erro = ["[sys] - Caminho não encontrado"]
            return erro
        
        try:
            # Descobrir tamanho da partição em bytes
            tamanho_particao = path.getsize(endereco_particao)

            # Calculando setores por tabela
            # Setores por tabela = RoundUp(TotalClusters * TamEntradaFAT / BytesPorSetor)
            
            total_clusters = (tamanho_particao / bytes_por_setor) / setores_por_cluster
            bytes_por_entrada = 32 / 4 # 32 bits de entrada FAT -> 4 bytes

            tamannho_fat_bytes = total_clusters * ceil(bytes_por_entrada)

            setores_por_tabela = ceil(tamannho_fat_bytes / bytes_por_setor)       

            # Execução da formatação
            formatador = Formatador()
            formatador.formatar_completo(
                endereco_particao, 
                tamanho_particao, 
                bytes_por_setor, 
                setores_por_tabela, 
                setores_por_cluster, 
                num_entradas_raiz
            )

            # Guardar os novos dados nos atributos privados (Estado do Sistema)
            self.set_bytes_por_setor(bytes_por_setor)
            self.set_setores_por_tabela(setores_por_tabela)
            self.set_setores_por_cluster(setores_por_cluster)
            self.set_num_entradas_raiz(num_entradas_raiz)
            self.set_endereco_particao(endereco_particao)
            self.set_tamanho_total_particao(tamanho_particao)

            return [f"[sys] - Partição em {endereco_particao} formatada com sucesso."]

        except Exception as e:
            return [f"[sys] - Erro inesperado: {str(e)}"]