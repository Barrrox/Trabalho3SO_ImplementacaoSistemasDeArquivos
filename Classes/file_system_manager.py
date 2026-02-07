import math
import os

from Classes.FAT_table_manager import FAT_table_manager
from Classes.disk_manager import disk_manager
from Classes.root_dir_manager import root_dir_manager
from Classes.data_manager import data_manager
from Formatador.formatador import Formatador

class FileSystemManager:
    
    def __init__(self):
    # Inicializa os atributos do Boot Record
    # self._<atributo> representa um atributo PRIVATE  # FIX: Ajustar pra ler do formator
       
       # valores fixos
        self.__bytes_por_setor     = 512    # 2 bytes
        self.__setores_por_tabela  = 131072 # 4 bytes
        
        # valores variáveis
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
        retorna o número de bytes por setor
        """

        return self.__bytes_por_setor
#*******************************************************************************************************#
    def get_setores_por_tabela(self):
        return self.__setores_por_tabela
#*******************************************************************************************************#
    def get_setores_por_cluster(self):
        return self.__setores_por_cluster 
#*******************************************************************************************************#
    def get_num_entradas_raiz(self):
        """
        retorna o número de entradas do root dir
        """
        return self.__num_entradas_raiz
#*******************************************************************************************************# 
    def get_endereco_particao(self):
        """Retorna o caminho do arquivo .bin atual"""
        return self.__endereco_particao
#*******************************************************************************************************#    
    def get_tamanho_total_particao(self):
        """Retorna o tamanho total da particao em bytes"""
        return self.__tamanho_total_particao
#*******************************************************************************************************# 
    def get_total_clusters(self):
        """
        Retorna o total de clusters na partição
        """

        tamanho_particao = self.get_tamanho_total_particao()
        bytes_por_setor = self.get_bytes_por_setor()
        setores_por_cluster = self.get_setores_por_cluster()

        total_clusters = (tamanho_particao / bytes_por_setor) / setores_por_cluster

        return int(total_clusters)
#*******************************************************************************************************# 
    def get_offset(self, secao):
        """
        Retorna o offset em binario de uma seção do BootRecord. O parâmetro seção pode deve ser
        uma das seguintes strings: "boot_record", "fat1", "fat2", "root_dir", "area_dados"
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
        retorna o tamanho em bytes de 1 cluster na configuração atual
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
        Define o tamanho total da partição em bytes
        Garante que o tamanho seja um valor numérico positivo.
        """
        if isinstance(tamanho, (int, float)) and tamanho >= 0:
            self.__tamanho_total_particao = tamanho
        return    
#*******************************************************************************************************#    
    def set_bytes_por_setor(self, bytes_por_setor):
        """
        retorna o número de bytes por setor
        """

        self.__bytes_por_setor = bytes_por_setor

        return    
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

        if args[0] == "1":
            return {"rodou?": True, "comando" : "exemplo2", "dados" : 1, "msg_erro": None}
        else:
            return {"rodou?": False, "comando" : "exemplo2", "dados" : None, "msg_erro": "Não digitou 1"}
#*******************************************************************************************************#   
    # deletar nome_arqv
    def comando_deletar(self, *args):
        
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
        1 - Identificar o tipo de cópia 
            - 1.1 Cópia interna (para dentro) : comparar args[0] e <insira string de path para o endereço da partição>
            - 1.2 Cópia externa (de/para o .bin) : else da comparação acima

        1.1 - Cópia Interna
            - Verificar se o arquivo de origem existe : comando_listar + root_dir_manager.ler_entrada()
            - Verificar se há espaço disponível na partição : fat_manager.verificar_espaco_disponivel(tamanho_arquivo)
            - Se espaço, alocar FAT : fat_manager.alocar_entradas_FAT(tamanho_arquivo)
                - Alocar entrada no root directory : 
                - Copiar dados para os clusters alocados : pega o retorno da alocação FAT que contém a posição relativa das entradas alocadas e escreve os dados via data_manager.escrever_dados()
        
        1.2 - Cópia Externa
            - Verificar se o arquivo de origem existe nesse sistema
                Alternativa 1 - Verificar se há espaço disponível na partição
                Alternativa 2 - Tentar copiar direto e verificar o retorno para saber se foi ou deu erro

        2 - Verificar se é um diretório ou arquivo único 
            2.1 - Se diretório, acionar FLAG
            
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
        Copia um arquivo ou diretorio de fora do sistema de arquivos(SO) para dentro

        Parâmetros:
            caminho_origem: path absoluto do arquivo dentro do SO

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
    
    def funcao_copiar_externa(self, caminho_origem, caminho_destino):
        """
        Copia um arquivo ou diretorio de dentro do sistema de arquivos para fora

        Parâmetros:
            caminho_origem: path absoluto do arquivo dentro do sitema de arquivos
            caminho_destino: path absoluto do arquivo fora do sistema de arquivos

        Retorna: 

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
        comando_formatar operacionaliza a formatação da partição

        args:
            endereco_particao: path absoluto para o endereço da partição
            bytes_por_setor: quantidade de bytes por setor desejada
            setores_por_cluster: setores por cluster desejados
            num_entradas_raiz: numero de entradas no root dir desejado

        Retornos:
            Lista com uma mensagem de sucesso caso sucesso na formatação
            Lista com uma mensagem de erro caso falha
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