
class root_dir_manager:

    def __init__(self, file_sys_manager):

        self.file_sys_manager = file_sys_manager

    def escrever_entrada_arquivo(self, atributo, nome : str, extensao : str, tamanho, primeiro_cluster, dono = None, nivel_de_acesso = None):        
        
        # verificação se o arquiivo já existe
        entrada_existente = self.ler_entrada(nome, extensao)
        if entrada_existente is not None:
            raise Exception("Erro: Entrada com o mesmo nome e extensão já existe.")
        
        
        # Verificação prévia de adequação ao sistema
        if tamanho > (2**32 -1):
            raise Exception("Erro: Tamanho do arquivo excede o limite máximo de 4GB.")
        if len(nome) > 8:
            raise Exception("Erro: Nome do arquivo excede o limite máximo de 8 caracteres.")
        if len(extensao) > 3:
            raise Exception("Erro: Extensão do arquivo excede o limite máximo de 3 caracteres.")

        
        offset_root_dir = self.file_sys_manager.get_offset("root_dir")
        caminho_particao = self.file_sys_manager.get_endereco_particao()
        num_entradas = self.file_sys_manager.get_num_entradas_raiz()


        with open(caminho_particao, "r+b") as f:
            f.seek(offset_root_dir)

            # Encontrar a primeira entrada livre (atributo 0x00 ou 0x01)

            for _ in range(num_entradas):
                
                byte_array = f.read(22)  # Cada entrada tem 22 bytes
                
                posicao_atual = f.tell() # salva a posição da entrada sendo lida
                checkar_leitura = posicao_atual

                if byte_array[0] == 0x0: # encontrou uma entrada livre
                    f.seek(posicao_atual - 22)  # Volta para o início da entrada livre # testar
                    # Prepara os dados para escrita
        
                    atributo_bytes     = atributo.to_bytes(1, 'little')               
                    nome_binario       = ' '.join('{0:08b}'.format(ord(x), 'b') for x in nome)
                    extensao_binario   = ' '.join('{0:08b}'.format(ord(x), 'b') for x in extensao)
                    tamanho_bytes      = tamanho.to_bytes(4, 'little')
                    dono_bytes         = dono.to_bytes(1, 'little')
                    nivel_acesso_bytes = nivel_de_acesso.to_bytes(1, 'little')
                #   primeiro_cluster já deve estar em binário (posição absoluta)

                    # Escreve os dados na entrada livre
                    f.write(atributo_bytes)
                    f.write(nome_binario)
                    f.write(extensao_binario)
                    f.write(tamanho_bytes)
                    f.write(dono_bytes)
                    f.write(nivel_acesso_bytes)
                    f.write(primeiro_cluster)  

                    if f.tell() != checkar_leitura: # algo deu errado na escrita # tratar a exclusao de tudo relacionado ao arquivo
                        self.file_sys_manager.tratar_erros.tratar_erro_escrita_entrada_root_dir(nome, extensao) # tentar apagar a entrada escrita
                        
                    else:
                        break # escrita deu certo, sai do loop
                else:
                    continue # continua procurando uma entrada livre

        return True # escreveu com sucesso            

    def ler_entrada(self, nome_arquivo : str, extensao_arquivo : str):
        """
        Procura e retorna os atributos de uma entrada. Retorno:
        
        [atributo, nome, extensao, tamanho, dono, nivel_acesso, primeiro_cluster]
        """
        # 1. Pega infos necessarias do file sys manager
        offset_root_dir = self.file_sys_manager.get_offset("root_dir")
        caminho_particao = self.file_sys_manager.get_endereco_particao()
        num_entradas = self.file_sys_manager.get_num_entradas_raiz()

        # Formata para comparação exata (geralmente nomes em FAT são preenchidos com espaços)
        nome_busca = nome_arquivo.lower()
        ext_busca = extensao_arquivo.lower()

        with open(caminho_particao, "rb") as f:
            f.seek(offset_root_dir)

            for _ in range(num_entradas):
                entrada_buffer = f.read(22) # Cada entrada tem 22 bytes

                if entrada_buffer[0] == 0x00 or entrada_buffer[0] == 0x01:
                    continue

                # Decodifica apenas campos que são strings (Nome e Extensão)
                nome = entrada_buffer[1:9].decode('utf-8').strip().lower()
                extensao = entrada_buffer[9:12].decode('utf-8').strip().lower()

                if nome == nome_arquivo.lower() and extensao == extensao_arquivo.lower():
                    atributo = entrada_buffer[0:1] # Mantém como byte ou converte para int
                    tamanho = int.from_bytes(entrada_buffer[12:16], 'little')
                    dono = int.from_bytes(entrada_buffer[16:18], 'little')
                    nivel_acesso = int.from_bytes(entrada_buffer[18:20], 'little')
                    primeiro_cluster = int.from_bytes(entrada_buffer[20:22], 'little')
                    
                    return [atributo, nome, extensao, tamanho, dono, nivel_acesso, primeiro_cluster]
                                
        return None
    
    def listar_entradas():
        # lista todas as entradas do diretório
        # ignorar entradas com atributo 0x01 (oculto ou excluído)
        # output = [(nome, extensao), (nome, extensao)]
        return

    def procurar_entrada_livre(self):
        # procura uma entrada disponível no root dir
        # retorna a posição absoluta dessa entrada
        offset_root_dir = self.file_sys_manager.get_offset("root_dir")
        caminho_particao = self.file_sys_manager.get_endereco_particao()
        num_entradas = self.file_sys_manager.get_num_entradas_raiz()

        with open(caminho_particao, "rb") as f:
            f.seek(offset_root_dir)

            for _ in range(num_entradas):
                
                byte_array = f.read(22)  # Cada entrada tem 22 bytes
                posicao_atual = f.tell() # salva a posição da entrada sendo lida

                if byte_array[0] == 0x0: # encontrou uma entrada livre
                    f.seek(posicao_atual - 22)  # Volta para o início da entrada livre # testar
                    return posicao_atual
                else: # se não achou uma entrada livre, continua
                    pass
            return None