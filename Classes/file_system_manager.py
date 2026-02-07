import math
import os

from Classes.FAT_table_manager import FAT_table_manager
from Classes.disk_manager import disk_manager
from Classes.root_dir_manager import root_dir_manager
from Classes.data_manager import data_manager
from Formatador.formatador import Formatador

class FileSystemManager:
    """
    Classe orquestradora do Sistema de Arquivos.
    Gerencia a comunicação entre a Interface (CLI) e os gerenciadores de baixo nível
    (Disk, FAT, RootDir, Data). Mantém o estado atual da partição montada.
    """
    
    def __init__(self):
        # Valores padrão (Boot Record)
        self.__bytes_por_setor     = 512    # 2 bytes
        self.__setores_por_tabela  = 131072 # 4 bytes
        
        # Valores variáveis
        self.__setores_por_cluster = 8      # 1 byte
        self.__num_entradas_raiz   = 512    # 2 bytes
        self.__endereco_particao = r"C:\Users\Usuario\Desktop\Unio\SO\TRAB3\Trabalho3SO_ImplementacaoSistemasDeArquivos\disco_virtual.bin"
        self.__tamanho_total_particao = 0
        self.__usuario = 1

        # Inicializa os managers que não tem dependências primeiro
        self.root_dir_manager = root_dir_manager(self)
        self.disk_manager = disk_manager(self)
        
        # Inicializa os managers que dependem dos anteriores
        self.data_manager = data_manager(self)
        self.fat_manager = FAT_table_manager(self)
      
#*******************************************************************************************************#
    def get_bytes_por_setor(self):
        """
        :return: int: O número de bytes por setor configurado.
        """
        return self.__bytes_por_setor
#*******************************************************************************************************#
    def get_setores_por_tabela(self):
        """
        :return: int: O número de setores ocupados por uma tabela FAT.
        """
        return self.__setores_por_tabela
#*******************************************************************************************************#
    def get_setores_por_cluster(self):
        """
        :return: int: A quantidade de setores que compõem um cluster.
        """
        return self.__setores_por_cluster 
#*******************************************************************************************************#
    def get_num_entradas_raiz(self):
        """
        :return: int: O número máximo de entradas permitidas no diretório raiz.
        """
        return self.__num_entradas_raiz
#*******************************************************************************************************# 
    def get_endereco_particao(self):
        """
        :return: str: O caminho absoluto do arquivo .bin (disco virtual).
        """
        return self.__endereco_particao
#*******************************************************************************************************#    
    def get_tamanho_total_particao(self):
        """
        :return: int: O tamanho total da partição em bytes.
        """
        return self.__tamanho_total_particao
#*******************************************************************************************************# 
    def get_total_clusters(self):
        """
        Calcula o total de clusters disponíveis na partição.
        
        :return: int: Número total de clusters.
        """
        tamanho_particao = self.get_tamanho_total_particao()
        bytes_por_setor = self.get_bytes_por_setor()
        setores_por_cluster = self.get_setores_por_cluster()

        total_clusters = (tamanho_particao / bytes_por_setor) / setores_por_cluster

        return int(total_clusters)
#*******************************************************************************************************# 
    def get_offset(self, secao):
        """
        Retorna o deslocamento (offset) em bytes onde inicia uma seção específica do disco.
        
        :param secao: pode ser qualquer string dentro dessa lista: ("boot_record", "fat1", "fat2", "root_dir", "area_dados")
        :return: int: Offset em bytes ou None se a seção for inválida.
        """
        bytes_setor = self.get_bytes_por_setor()
        setores_por_tabela = self.get_setores_por_tabela()
        numero_entradas_raiz = self.get_num_entradas_raiz()
        tamanho_entrada_root_dir = 22  # tamanho de cada entrada em bytes

        if secao == "boot_record":
            return 0
        
        elif secao == "fat1":
            return bytes_setor  # offset boot record
        
        elif secao == "fat2":
            return bytes_setor + (setores_por_tabela * bytes_setor)  # offset boot record + tabela FAT 1
        
        elif secao == "root_dir":
            return bytes_setor + ( (setores_por_tabela * bytes_setor) * 2) # offset boot record + 2 tabelas FAT
        
        elif secao == "area_dados":
            return (bytes_setor + ( (setores_por_tabela * bytes_setor) * 2) +
                    (numero_entradas_raiz * tamanho_entrada_root_dir))  # offset root dir + tamanho root dir
        
        else:
            return None
#*******************************************************************************************************#
    def get_tamanho_cluster(self):
        """
        Calcula o tamanho de um cluster baseado na configuração atual.
        Fórmula: bytes_por_setor * setores_por_cluster
        
        :return: int: Tamanho do cluster em bytes.
        """

        tamanho_setor = self.get_bytes_por_setor()
        setores_por_cluster = self.get_setores_por_cluster()

        tamanho_cluster = tamanho_setor*setores_por_cluster
        
        return tamanho_cluster
#*******************************************************************************************************#
    def get_usuario(self):
        """Retorna o usuario atual do sistema"""
        return self.__usuario
#*******************************************************************************************************#
    def get_nivel_permissao(self):

        usuario = self.get_usuario()

        if usuario == "admin" or usuario == "administrador":
            return 1
        else:
            return 0
#*******************************************************************************************************#
    def set_usuario(self, usuario):
        self.__usuario = usuario
#*******************************************************************************************************
    def set_setores_por_tabela(self, setores_por_tabela):
        self.__setores_por_tabela = setores_por_tabela
        return
#*******************************************************************************************************#
    def set_num_entradas_raiz(self, num_entradas_raiz):
        self.__num_entradas_raiz = num_entradas_raiz
        return
#*******************************************************************************************************#  
    def set_setores_por_cluster(self, setores_por_cluster):
        self.__setores_por_cluster = setores_por_cluster
        return
#*******************************************************************************************************#
    def set_tamanho_total_particao(self, tamanho):
        """
        Define o tamanho total da partição.
        
        :param tamanho: int ou float (será tratado como bytes). Deve ser >= 0.
        """
        if isinstance(tamanho, (int, float)) and tamanho >= 0:
            self.__tamanho_total_particao = tamanho
        return    
#*******************************************************************************************************#    
    def set_bytes_por_setor(self, bytes_por_setor):
        """
        Define a quantidade de bytes por setor.
        :param bytes_por_setor: int
        """
        self.__bytes_por_setor = bytes_por_setor

        return    
#*******************************************************************************************************#
    def set_endereco_particao(self, endereco):
        """
        Define o endereço do arquivo de disco.
        
        :param endereco: str: Caminho do arquivo.
        :return: bool: True se o endereço for uma string válida, False caso contrário.
        """
        if isinstance(endereco, str):
            self.__endereco_particao = endereco
            return True
        return False
#*******************************************************************************************************#   
    def ler_input_interface(self, input_string):
        """
        Processa a entrada bruta do usuário e encaminha para o disparador.
        
        :param input_string: str: O comando completo digitado (ex: "copiar a.txt b.txt")
        :return: list: Lista contendo strings de feedback ou mensagens de erro.
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
        Identifica e executa o método correspondente ao comando solicitado usando reflection.
        Ex: "deletar" -> busca por self.comando_deletar
        
        :param stringComando: list: [comando, arg1, arg2, ...]
        :return: list: Retorno do método executado ou mensagem de erro.
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

        if args[0] == "1":
            return {"rodou?": True, "comando" : "exemplo2", "dados" : 1, "msg_erro": None}
        else:
            return {"rodou?": False, "comando" : "exemplo2", "dados" : None, "msg_erro": "Não digitou 1"}
#*******************************************************************************************************#   
    # deletar nome_arqv
    def comando_deletar(self, *args):
        """
        Remove um arquivo do sistema (Root Dir e FAT).
        
        :param args: tuple: (nome_arquivo_com_extensao,)
        :return: list: Mensagem de sucesso ou erro.
        """
        
        if not args:
            return ["[sys] - Erro: Informe o arquivo a ser deletado."]
            
        arquivo_str = args[0].lower()
        
        # Validação de extensão
        if "." not in arquivo_str:
            return ["[sys] - Informe o nome e a extensão (ex: arquivo.txt)"]

        # 1. Separa Nome e Extensão (Correção do erro atual)
        nome_arquivo = arquivo_str.split(".")[0]
        extensao_arquivo = arquivo_str.split(".")[1]
        
        entrada = self.root_dir_manager.ler_entrada(nome_arquivo, extensao_arquivo) # procura entrada do arquivo

        if not entrada:
            return ["[sys] - Arquivo não encontrado"]

        # entrada = [atributo, nome, extensao, tamanho, dono, nivel_de_acesso, primeiro_cluster]
        primeiro_cluster = entrada[6]

        self.fat_manager.desalocar_arquivo(primeiro_cluster) 
        self.root_dir_manager.desalocar_entrada_arquivo(nome_arquivo) 
        self.fat_manager.sincronizar_fat_1_2()

        return [f"arquivo {arquivo_str} excluido"]
#*******************************************************************************************************#
    def comando_bootrecord(self):
        """
        Coleta as informações atuais do Boot Record (parâmetros de formatação).
        
        :return: list: Lista de strings formatadas com as informações.
        """

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
    # args[0] = origem
    # args[1] = destino

    def comando_copiar(self, *args): # copia os elementos
        """
        Gerencia operações de cópia (Importação e Exportação).
        
        Uso:
            1. Importar (PC -> Sistema): copiar <caminho_arquivo_pc>
            2. Exportar (Sistema -> PC): copiar <arquivo_interno> <caminho_destino_pc>
            
        :param args: tuple: Argumentos passados pela CLI.
        :return: list: Mensagem de feedback ou erro.
        """
    # args[0] = origem
    # args[1] = destino

        if not args:
            return ["[sys] - Erro: Faltam argumentos."]
        
        if len(args) > 2:
            return ["[sys] - Número incorreto de argumentos."]

        caminho_origem = args[0]

        # === CENÁRIO 1: EXPORTAR (Virtual -> PC) ===
        # Se tem 2 argumentos, é cópia externa (Saída)
        if len(args) == 2:
            caminho_destino = args[1]
            retorno = self.funcao_copiar_externa(caminho_origem, caminho_destino)
            
            if retorno is None:
                return [f"[sys] - Arquivo '{caminho_origem}' exportado para '{caminho_destino}'."]
            return retorno

        # === CENÁRIO 2: IMPORTAR (PC -> Virtual) ===
        # Se tem 1 argumento, é cópia interna (Entrada)
        elif len(args) == 1:

            # Verifica se existe
            if not os.path.exists(caminho_origem):
                return ["[sys] - Arquivo de origem não encontrado"]
            
            retorno = self.funcao_copiar_interna(caminho_origem)
            
            if retorno is None:
                 return [f"[sys] - Arquivo '{caminho_origem}' importado com sucesso."]
            return retorno

    def funcao_copiar_interna(self, caminho_origem):
        """
        Realiza a importação: Copia um arquivo do SO (host) para o disco virtual.
        
        :param caminho_origem: str: Path absoluto do arquivo no computador host.
        :return: list ou None: Retorna lista com mensagem de erro em caso de falha, ou None em sucesso.
        """

        # Pega nome e extensão do arquivo#
        arquivo_str = caminho_origem.split("/")[-1].lower()
        nome_arquivo     = arquivo_str.split(".")[0].lower()
        extensao_arquivo = arquivo_str.split(".")[1].lower()
        
        # Le a entrada
        entrada = self.root_dir_manager.ler_entrada(nome_arquivo, extensao_arquivo)

        if entrada != None:
            erro = ['[sys] - Arquivo já existe no sistema. Operação abortada']
           # print("Arquivo já existe")
            return erro

        if isinstance(entrada, str):
            erro = entrada # retorna a string de erro providenciada pela função ler_entrada
            return erro
        
        tamanho_arquivo = os.path.getsize(caminho_origem)

        #************************************************************# começo da alocação

        if self.fat_manager.verificar_espaco_disponivel(tamanho_arquivo): # testa se tem espaço disponível para o arquivo
            tamanho_cluster = self.get_tamanho_cluster()

            quantidade_de_clusters = math.ceil(tamanho_arquivo/tamanho_cluster)       

            entradas, __Error = self.fat_manager.buscar_entradas_livres(quantidade_de_clusters)
            
            if len(entradas) == quantidade_de_clusters: #  se tem entradas o bastante disponíveis
                
                entrada_root_dir = self.root_dir_manager.procurar_entrada_livre() # testa se existe uma entrada disponível
                
                if entrada_root_dir != None: # se tiver 
                  
                    entradas = self.fat_manager.alocar_entradas_FAT(tamanho_arquivo)
                    escrita = self.root_dir_manager.escrever_entrada_arquivo(
                        atributo=0x02, 
                        nome=nome_arquivo, 
                        extensao=extensao_arquivo, 
                        tamanho=tamanho_arquivo, 
                        primeiro_cluster=entradas[0], 
                        dono=self.get_usuario(), 
                        nivel_de_acesso=self.get_nivel_permissao())
                    
                    
                    if not escrita:
                        print(f"escreveu errado")
                        #  escreveu errado, falta tratar
                        pass
                    # como tem espaço no disco e entrada no root, lemos o arquivo:

                    with open(caminho_origem, 'rb') as f:
                        dados_arquivo = f.read()
                    
                    self.data_manager.alocar_cluster(entradas, dados_arquivo)
                    

                # verificar se tem espaço disponível no root dir
            
        else:
            error = ["[sys] - Não há espaço disponível no sistema. Operação abortada"]
            return error
        
        self.fat_manager.sincronizar_fat_1_2()
    
    def funcao_copiar_externa(self, caminho_origem, caminho_destino):
        """
        Realiza a exportação: Copia um arquivo do disco virtual para o SO (host).

        :param caminho_origem: str: Nome do arquivo dentro do disco virtual.
        :param caminho_destino: str: Path de destino no computador host.
        :return: list ou None: Retorna lista com mensagem de erro em caso de falha, ou None em sucesso.
        """
        
        # 1. Pegar o nome do arquivo (Funciona em Windows e Linux)
        # os.path.basename pega apenas "arquivo.txt" ignorando C:\ ou /home/
        arquivo_str = os.path.basename(caminho_origem).lower()

        if "." not in arquivo_str:
             return ["[sys] - Arquivo sem extensão não suportado"]
        
        nome_arquivo = arquivo_str.split(".")[0]
        extensao_arquivo = arquivo_str.split(".")[1]

        # 1.1 Ler entrada no root dir
        entrada_arquivo = self.root_dir_manager.ler_entrada(nome_arquivo, extensao_arquivo)

        if not entrada_arquivo:
            erro = ["[sys] - Arquivo de origem não encontrado"]
            return erro

        # 1.2 Pegar cluster via tabela FAT
        primeiro_cluster = entrada_arquivo[6]
        clusters_arquivo = self.fat_manager.pegar_clusters_arquivo(primeiro_cluster)

        # 1.3 ler arquivo via data manager
        dados_arquivo = self.data_manager.ler_clusters(clusters_arquivo)

        # Se o data_manager retornar uma string (mensagem de erro), não podemos gravar
        if isinstance(dados_arquivo, str) and "[sys]" in dados_arquivo:
             return [dados_arquivo]
        
        # 2. Copiar buffer para o destino
        with open(caminho_destino, 'wb') as f:
            f.write(dados_arquivo)

        return 
    
#*******************************************************************************************************#
    def comando_listar(self): # lista os elementos do diretório
        """
        Lista os arquivos e diretórios presentes no diretório raiz.
        
        :return: list: Lista de strings com os nomes dos arquivos (ex: ["a.txt", "b.png"]).
        """
        
        entradas = self.root_dir_manager.listar_entradas()

        if not entradas:
            erro = ["[sys] - Diretório vazio"]
            return erro
        
        resultado = []
        for entrada in entradas:
            resultado.append(f"{entrada[0]}.{entrada[1]}")
        
        return resultado
#*******************************************************************************************************#    
    def comando_formatar(self, *args):
        """
        Formata a partição com o sistema de arquivos FAT48, definindo a geometria do disco.
        
        :param args: tuple contendo:
            0: endereco_particao (str)
            1: bytes_por_setor (int)
            2: setores_por_cluster (int)
            3: num_entradas_raiz (int)
            
        :return: list: Mensagem de sucesso ou erro.
        """
        # 1. Inicialização de variáveis via argumentos
        endereco_particao = args[0].strip('\'"')
        
        endereco_particao = os.path.normpath(endereco_particao)

        #endereco_particao = args[0]

        bytes_por_setor     = int(args[1])
        setores_por_cluster = int(args[2])
        num_entradas_raiz   = int(args[3])

        # 2. Verificar se caminho válido
        if not os.path.exists(endereco_particao):
            erro = ["[sys] - Caminho não encontrado"]
            return erro
        
        try:
            # 3. Descobrir tamanho da partição em bytes
            tamanho_particao = os.path.getsize(endereco_particao)

            # 4. Calculando setores por tabela
            # Setores por tabela = RoundUp(TotalClusters * TamEntradaFAT / BytesPorSetor)

            total_clusters = tamanho_particao / bytes_por_setor / setores_por_cluster

            

            bytes_por_entrada = 32 / 8 # 32 bits de entrada FAT -> 4 bytes

            tamannho_fat_bytes = total_clusters * math.ceil(bytes_por_entrada)

            setores_por_tabela = math.ceil(tamannho_fat_bytes / bytes_por_setor)       

            # 6. Guardar os novos dados nos atributos privados (Estado do Sistema)
            self.set_bytes_por_setor(int(bytes_por_setor))
            self.set_setores_por_tabela(int(setores_por_tabela))
            self.set_setores_por_cluster(int(setores_por_cluster))
            self.set_num_entradas_raiz(int(num_entradas_raiz))
            self.set_endereco_particao(endereco_particao)
            self.set_tamanho_total_particao(int(tamanho_particao))

            
            # 5. Execução da formatação
            formatador = Formatador()
            formatador.formatar_completo(
                endereco_particao, 
                int(tamanho_particao), 
                int(bytes_por_setor), 
                int(setores_por_tabela), 
                int(setores_por_cluster), 
                int(num_entradas_raiz)
            )
            
            self.set_endereco_particao(endereco_particao)
            return [f"[sys] - Partição em {endereco_particao} formatada com sucesso."]
        
        

        except Exception as e:
            return [f"[sys] - Erro inesperado: {str(e)}"]