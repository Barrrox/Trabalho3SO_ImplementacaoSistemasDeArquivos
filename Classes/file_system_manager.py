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
        self.__bytes_por_setor     = 512                        # 2 bytes # ALTERAR PARA FSEEK DE ARQUIVO DPS, HARDCODE SO PARA TESTE
        self.__setores_por_tabela  = 131072                  # 4 bytes
        self.__setores_por_cluster = 8                      # 1 byte
        self.__num_entradas_raiz   = 512                 # 2 bytes
        
        # Inicializa os managers que não tem dependências primeiro
        self.root_dir_manager = root_dir_manager()
        self.disk_manager = disk_manager(self)
        
        # Inicializa os managers que dependem dos anteriores
        self.data_manager = data_manager(self)
        self.fat_manager = FAT_table_manager(self)
        
        
        self.endereco_particao = None
        
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
    def get_offset(self, secao):
        """
        Retorna o offset (inteiro) em bytes de uma seção do BootRecord. O parâmetro seção pode deve ser
        uma das seguintes strings: "boot_record", "fat1", "fat2", "root_dir", "area_dados"
        """
        bytes_setor = self.file_sys_manager.get_bytes_por_setor()
        setores_por_tabela = self.file_sys_manager.get_setores_por_tabela()
        numero_entradas_raiz = self.file_sys_manager.get_num_entradas_raiz()
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
    def comando_exemplo2(self, *argumento_teste):

        if argumento_teste == 1:
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

    def comando_mover(self): # move elemento de um diretório para outro
        return
    
    def comando_formatar(self):
        # Pegar inputs do usuário

        print("Iniciando questionário de formatação")

        caminho_particao = input("\nInsira o caminho para a partição: ")

        # Verificar se caminho válido
        if not path.exists(caminho_particao):
            erro = ["[sys] - Caminho não encontrado"]
            return erro
        
        try:
            # Descobrir tamanho do disco em bytes
            tamanho_particao = path.getsize()

            # Capturar inputs do usuário
            bytes_por_setor = int(input("\nBytes por setor: "))
            setores_por_cluster = int(input("\nSetores por cluster: "))
            num_entradas_raiz = int(input("\nNúmero de entrada da raiz: "))

            # Calculando setores por tabela
            # Setores por tabela = RoundUp(TotalClusters * TamEntradaFAT / BytesPorSetor)
            
            total_clusters = (tamanho_particao/bytes_por_setor)/setores_por_cluster
            bytes_por_entrada = 32/4 # 32 bits de entrada FAT -> 4 bytes

            tamannho_fat_bytes = total_clusters * ceil(bytes_por_entrada)

            setores_por_tabela = ceil(tamannho_fat_bytes / bytes_por_setor)       

            # Confirmar escolhas
            print("\n\nConfiguração escolhida")
            print(f"\n  bytes por setor: {bytes_por_setor}")
            print(f"\n  setores por cluster: {setores_por_cluster}")
            print(f"\n  numero de entradas da raiz: {num_entradas_raiz}")

            print("\n\nSistema")        
            print(f"\n  setores por tabela: {setores_por_tabela} setores")
            print(f"\n  tamanho da partição: {tamanho_particao} bytes")
            
            confirmar = input("\nConfirmar formatação (s/n): ")

            while confirmar not in ["s", "n"]:
                confirmar = input("\nConfirmar formatação (s/n): ")

            
            if confirmar == "n":
                erro = ["[sys] - Formatação cancelada pelo usuário"]
                return erro

            else:
                print("\nInicinado formatação...")

                # Instancia e chama o formatador
                formatador = Formatador()

                formatador.formatar_completo(caminho_particao, tamanho_particao, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz)

                # Guardar os novos dados
                self.__bytes_por_setor = bytes_por_setor
                self.__setores_por_tabela = setores_por_tabela
                self.__setores_por_cluster = setores_por_cluster
                self.__num_entradas_raiz = num_entradas_raiz
                self.endereco_particao = caminho_particao

        except Exception as e:
            return [f"[sys] - Erro inesperado: {str(e)}"]

        return 