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
    Mantém o estado da partição e gerencia a comunicação entre a CLI e os módulos de baixo nível.
    """
    
    def __init__(self):
        
        # Valores padrão (Boot Record)
        self.__bytes_por_setor     = 512    # 2 bytes
        self.__setores_por_tabela  = 131072 # 4 bytes
        
        # valores variáveis
        self.__setores_por_cluster = 8      # 1 byte
        self.__num_entradas_raiz   = 512    # 2 bytes
        self.__endereco_particao = r"C:\Users\mathe\Documentos\Ciência da Computação\3 ano\SO\Trabalho 3 - Sistema de Arquivos\Parte 2 - Implementação\disco_virtual.bin"
        self.__tamanho_total_particao = 0
        self.__usuario = 1

        # Inicializa os managers que não tem dependências circulares primeiro
        self.root_dir_manager = root_dir_manager(self)
        self.disk_manager = disk_manager(self)
        
        # Inicializa os managers que dependem dos anteriores
        self.data_manager = data_manager(self)
        self.fat_manager = FAT_table_manager(self)
      
#*******************************************************************************************************#
    def get_bytes_por_setor(self):
        """
        :return: int: Número de bytes por setor.
        """
        return self.__bytes_por_setor

#*******************************************************************************************************#
    def get_setores_por_tabela(self):
        """
        :return: int: Número de setores por tabela FAT.
        """
        return self.__setores_por_tabela

#*******************************************************************************************************#
    def get_setores_por_cluster(self):
        """
        :return: int: Número de setores por cluster.
        """
        return self.__setores_por_cluster 

#*******************************************************************************************************#
    def get_num_entradas_raiz(self):
        """
        :return: int: Número máximo de entradas no diretório raiz.
        """
        return self.__num_entradas_raiz

#*******************************************************************************************************# 
    def get_endereco_particao(self):
        """
        :return: str: Caminho absoluto do arquivo da partição.
        """
        return self.__endereco_particao

#*******************************************************************************************************#    
    def get_tamanho_total_particao(self):
        """
        :return: int: Tamanho total da partição em bytes.
        """
        return self.__tamanho_total_particao

#*******************************************************************************************************# 
    def get_total_clusters(self):
        """
        Retorna o total de clusters na partição.
        :return: int
        """
        tamanho_particao = self.get_tamanho_total_particao()
        bytes_por_setor = self.get_bytes_por_setor()
        setores_por_cluster = self.get_setores_por_cluster()

        if bytes_por_setor == 0 or setores_por_cluster == 0:
            return 0

        total_clusters = (tamanho_particao / bytes_por_setor) / setores_por_cluster

        return int(total_clusters)

#*******************************************************************************************************# 
    def get_offset(self, secao):
        """
        Retorna o offset em bytes de uma seção específica.
        
        :param secao: str ("boot_record", "fat1", "fat2", "root_dir", "area_dados")
        :return: int: Offset em bytes ou None se inválido.
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
        :return: int: Tamanho de 1 cluster em bytes.
        """
        tamanho_setor = self.get_bytes_por_setor()
        setores_por_cluster = self.get_setores_por_cluster()

        tamanho_cluster = tamanho_setor * setores_por_cluster
        
        return tamanho_cluster

#*******************************************************************************************************#
    def get_usuario(self):
        """
        :return: Usuário atual do sistema.
        """
        return self.__usuario

#*******************************************************************************************************#
    def get_nivel_permissao(self):
        """
        :return: int: 1 se admin, 0 caso contrário.
        """
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

#*******************************************************************************************************#
    def set_num_entradas_raiz(self, num_entradas_raiz):
        self.__num_entradas_raiz = num_entradas_raiz

#*******************************************************************************************************#  
    def set_setores_por_cluster(self, setores_por_cluster):
        self.__setores_por_cluster = setores_por_cluster

#*******************************************************************************************************#
    def set_tamanho_total_particao(self, tamanho):
        """
        Define o tamanho total da partição em bytes.
        :param tamanho: int ou float (>= 0).
        """
        if isinstance(tamanho, (int, float)) and tamanho >= 0:
            self.__tamanho_total_particao = tamanho
 
#*******************************************************************************************************#    
    def set_bytes_por_setor(self, bytes_por_setor):
        self.__bytes_por_setor = bytes_por_setor

#*******************************************************************************************************#
    def set_endereco_particao(self, endereco):
        """
        Define o endereço da partição.
        :param endereco: str
        :return: bool: True se válido.
        """
        if isinstance(endereco, str):
            self.__endereco_particao = endereco
            return True
        return False

#*******************************************************************************************************#   
    def ler_input_interface(self, input_string, callback=None):
        """
        Processa o input da interface.
        :param input_string: Comando completo digitado.
        :param callback: Função para atualização de progresso visual.
        """
        strings_unitarias = input_string.split()

        if not strings_unitarias:
            erro = ["Comando inválido ou não existente!"]
            return erro
        else:
            # Passa o callback adiante
            return self.disparar_comando(strings_unitarias, callback) 

#*******************************************************************************************************# 
    def disparar_comando(self, stringComando, callback=None): # Adicionado parametro
        """
        Executa dinamicamente o método correspondente.
        Passa o callback apenas se o comando for 'copiar' ou 'formatar'.
        """
        comando = stringComando[0]
        argumentos = stringComando[1:]
        
        comando_requerido = f"comando_{comando}"
        if hasattr(self, comando_requerido):
            metodo = getattr(self, comando_requerido)
            
            # Lógica para injetar o callback apenas onde é necessário
            if callback and comando in ["copiar", "formatar"]:
                return metodo(*argumentos, callback=callback)
            else:
                return metodo(*argumentos)
        else:
            erro = ["Comando inválido ou não existente!"]
            return erro

#*******************************************************************************************************#
    def comando_exemplo(self, *args):
        """Comando de teste (echo)."""
        resultado = [f"Comando de exemplo! você escreveu 'exemplo' seguido de {args}."]
        return resultado

#*******************************************************************************************************#
    def comando_exemplo2(self, *args):
        """Comando de teste (retorno dict)."""
        if args and args[0] == "1":
            return {"rodou?": True, "comando" : "exemplo2", "dados" : 1, "msg_erro": None}
        else:
            return {"rodou?": False, "comando" : "exemplo2", "dados" : None, "msg_erro": "Não digitou 1"}

#*******************************************************************************************************#   
    def comando_deletar(self, *args):
        """
        Deleta um arquivo do sistema.
        :param args: (nome_arquivo,)
        """
        
        if not args:
            return ["[sys] - Erro: Informe o arquivo a ser deletado."]
            
        arquivo_str = args[0].lower()
        
        # Validação de extensão
        if "." not in arquivo_str:
            return ["[sys] - Informe o nome e a extensão (ex: arquivo.txt)"]

        # 1. Separa Nome e Extensão
        nome_arquivo = arquivo_str.split(".")[0]
        extensao_arquivo = arquivo_str.split(".")[1]
        
        entrada = self.root_dir_manager.ler_entrada(nome_arquivo, extensao_arquivo)

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
        Exibe informações do Boot Record atual.
        :return: list: Info formatada.
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
    def comando_copiar(self, *args, callback=None):
        """
        Gerencia cópia de arquivos.
        
        Uso:
            1. Importar (PC -> Sistema): copiar <origem>
            2. Exportar (Sistema -> PC): copiar <origem> <destino>
            
        :param args: Argumentos da linha de comando.
        """

        if not args:
            return ["[sys] - Erro: Faltam argumentos."]
        
        if len(args) > 2:
            return ["[sys] - Número incorreto de argumentos."]

        caminho_origem = args[0]

        # === CENÁRIO 1: EXPORTAR (Virtual -> PC) ===
        if len(args) == 2:
            caminho_destino = args[1]
            retorno = self.funcao_copiar_externa(caminho_origem, caminho_destino)
            
            if retorno is None:
                return [f"[sys] - Arquivo '{caminho_origem}' exportado para '{caminho_destino}'."]
            return retorno

        # === CENÁRIO 2: IMPORTAR (PC -> Virtual) ===
        elif len(args) == 1:
            # Verifica se existe no PC
            if not os.path.exists(caminho_origem):
                return ["[sys] - Arquivo de origem não encontrado"]
            
            retorno = self.funcao_copiar_interna(caminho_origem, callback=callback) 

            if retorno is None:
                 return [f"[sys] - Arquivo '{caminho_origem}' importado com sucesso."]
            return retorno

    def funcao_copiar_interna(self, caminho_origem, callback=None):
        """
        Importa um arquivo do SO para o disco virtual.
        :param caminho_origem: Path absoluto no SO.
        """

        # Pega nome e extensão do arquivo
        arquivo_str = os.path.basename(caminho_origem).lower()
        if "." not in arquivo_str:
             return ["[sys] - Arquivos sem extensão não são suportados na importação."]

        nome_arquivo     = arquivo_str.split(".")[0].lower()
        extensao_arquivo = arquivo_str.split(".")[1].lower()
        
        # Le a entrada
        entrada = self.root_dir_manager.ler_entrada(nome_arquivo, extensao_arquivo)

        if isinstance(entrada, str):
                erro = entrada
                return erro
            
        elif entrada != None:
            erro = ['[sys] - Arquivo já existe no sistema. Operação abortada']
            return erro
        
        tamanho_arquivo = os.path.getsize(caminho_origem)

        #************************************************************# começo da alocação

        if self.fat_manager.verificar_espaco_disponivel(tamanho_arquivo): 
            tamanho_cluster = self.get_tamanho_cluster()
            quantidade_de_clusters = math.ceil(tamanho_arquivo/tamanho_cluster)       

            entradas, __Error = self.fat_manager.buscar_entradas_livres(quantidade_de_clusters)
            
            if len(entradas) == quantidade_de_clusters: 
                
                entrada_root_dir = self.root_dir_manager.procurar_entrada_livre()
                
                if entrada_root_dir != None: 
                  
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
                        #  escreveu errado, falta tratar
                        pass
                    
                    # Leitura e gravação dos dados
                    with open(caminho_origem, 'rb') as f:
                        dados_arquivo = f.read()
                    
                    self.data_manager.alocar_cluster(entradas, dados_arquivo, callback=callback)
                    
        else:
            error = ["[sys] - Não há espaço disponível no sistema. Operação abortada"]
            return error
        
        self.fat_manager.sincronizar_fat_1_2()
    
    def funcao_copiar_externa(self, caminho_origem, caminho_destino):
        """
        Exporta um arquivo do disco virtual para o SO.
        
        :param caminho_origem: Nome interno (ex: a.txt).
        :param caminho_destino: Path destino no SO.
        """
        
        # 1. Pegar o nome do arquivo
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

        tamanho_real = entrada_arquivo[3]  # tamanho salvo no root dir

        # 1.3 ler arquivo via data manager
        dados_arquivo = self.data_manager.ler_clusters(clusters_arquivo)

        dados_arquivo = dados_arquivo[:tamanho_real]

        # Se o data_manager retornar uma string, é erro
        if isinstance(dados_arquivo, str) and "[sys]" in dados_arquivo:
             return [dados_arquivo]
        
        # 2. Copiar buffer para o destino
        with open(caminho_destino, 'wb') as f:
            f.write(dados_arquivo)

        return 
    
#*******************************************************************************************************#
    def comando_listar(self):
        """
        Lista entradas do diretório raiz.
        :return: Lista de nomes formatados.
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
    def comando_formatar(self, *args, callback=None):
        """
        Formata a partição e atualiza os parâmetros do sistema.
        args: (endereco, bytes_setor, setores_cluster, num_entradas)
        """
        # 1. Inicialização de variáveis via argumentos
        endereco_particao = args[0].strip('\'"')
        endereco_particao = os.path.normpath(endereco_particao)

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
                int(num_entradas_raiz),
                callback=callback
            )
            
            self.set_endereco_particao(endereco_particao)
            return [f"[sys] - Partição em {endereco_particao} formatada com sucesso."]

        except Exception as e:
            return [f"[sys] - Erro inesperado: {str(e)}"]