class root_dir_manager:
    """
    Gerencia o Diretório Raiz (Root Directory), lidando com a criação, 
    leitura, listagem e exclusão lógica de entradas de arquivos e pastas.
    """

    def __init__(self, file_sys_manager):
        self.file_sys_manager = file_sys_manager

    def escrever_entrada_arquivo(self, atributo, nome: str, extensao: str, tamanho, primeiro_cluster, dono=0, nivel_de_acesso=0):        
        """
        Registra uma nova entrada de arquivo no diretório raiz.
        
        :param atributo: int: Valor do atributo (1 byte).
        :param nome: str: Nome do arquivo (máx 8 caracteres).
        :param extensao: str: Extensão do arquivo (máx 3 caracteres).
        :param tamanho: int: Tamanho do arquivo em bytes (máx 4GB).
        :param primeiro_cluster: int: Índice do cluster inicial na área de dados.
        :param dono: int: ID do proprietário.
        :param nivel_de_acesso: int: Nível de permissão.
        :return: bool ou str: True se sucesso, string com erro caso contrário.
        """
        entrada_existente = self.ler_entrada(nome, extensao)
        if entrada_existente is not None:
            return ("[sys] - Entrada com o mesmo nome e extensão já existe.")
        
        if tamanho > (2**32 - 1):
            return ("[sys] - Tamanho do arquivo excede o limite máximo de 4GB.")
        if len(nome) > 8:
            return ("[sys] - Nome do arquivo excede o limite máximo de 8 caracteres.")
        if len(extensao) > 3:
            return ("[sys] - Extensão do arquivo excede o limite máximo de 3 caracteres.")

        pos_entrada_livre = self.procurar_entrada_livre()
        if pos_entrada_livre is None:
            return ("[sys] - Não há entradas livres disponíveis no diretório raiz")
        
        caminho_particao = self.file_sys_manager.get_endereco_particao()

        with open(caminho_particao, "r+b") as f:
            f.seek(pos_entrada_livre)
            f.write(atributo.to_bytes(1, 'little'))
            f.write(nome.encode('utf-8').ljust(8, b' '))  # Preenche com espaços até 8 bytes
            f.write(extensao.encode('utf-8').ljust(3, b' '))  # Preenche com espaços até 3 bytes
            f.write(tamanho.to_bytes(4, 'little'))
            f.write(dono.to_bytes(1, 'little'))
            f.write(nivel_de_acesso.to_bytes(1, 'little'))
            f.write(primeiro_cluster.to_bytes(4, 'little')) 

        return True # escreveu com sucesso            

    def ler_entrada(self, nome_arquivo: str, extensao_arquivo: str = None):
        """
        Busca uma entrada específica e retorna seus metadados.
        
        :param nome_arquivo: str: Nome buscado.
        :param extensao_arquivo: str: Extensão buscada (None para diretórios).
        :return: list: [atributo, nome, extensao, tamanho, dono, nivel_acesso, primeiro_cluster] ou None.
        """
        if len(nome_arquivo) > 8:
            return ("[sys] - Nome do arquivo excede o limite máximo de 8 caracteres.")
        if extensao_arquivo and len(extensao_arquivo) > 3:
            return ("[sys] - Extensão do arquivo excede o limite máximo de 3 caracteres.")

        offset_root_dir = self.file_sys_manager.get_offset("root_dir")
        caminho_particao = self.file_sys_manager.get_endereco_particao()
        num_entradas = self.file_sys_manager.get_num_entradas_raiz()

        nome_busca = nome_arquivo.lower()
        ext_busca = extensao_arquivo.lower() if extensao_arquivo else None

        with open(caminho_particao, "rb") as f:
            f.seek(offset_root_dir)

            for _ in range(num_entradas):
                entrada_buffer = f.read(22) 

                if entrada_buffer[0] == 0x00 or entrada_buffer[0] == 0x01:
                    continue

                if ext_busca: # Tratamento como arquivo
                    nome = entrada_buffer[1:9].decode('utf-8').strip().lower()
                    extensao = entrada_buffer[9:12].decode('utf-8').strip().lower()
                else: # Tratamento como diretório
                    nome = entrada_buffer[1:9].decode('utf-8').strip().lower()
                    extensao = None

                if nome == nome_busca and extensao == ext_busca:
                    return [
                        entrada_buffer[0:1], # Atributo
                        nome,
                        extensao,
                        int.from_bytes(entrada_buffer[12:16], 'little'), # Tamanho
                        int.from_bytes(entrada_buffer[16:17], 'little'), # Dono
                        int.from_bytes(entrada_buffer[17:18], 'little'), # Acesso
                        int.from_bytes(entrada_buffer[18:22], 'little')  # Cluster
                    ]
        return None
    
    def listar_entradas(self):
        """
        Retorna uma lista resumida de todas as entradas válidas no diretório raiz.
        
        :return: list: Lista de tuplas (nome, extensao, tipo).
        """
        offset_root_dir = self.file_sys_manager.get_offset("root_dir")
        caminho_particao = self.file_sys_manager.get_endereco_particao()
        num_entradas = self.file_sys_manager.get_num_entradas_raiz()

        lista_retorno = []
        with open(caminho_particao, "rb") as f:
            f.seek(offset_root_dir)

            for _ in range(num_entradas):
                entrada_buffer = f.read(22)

                if entrada_buffer[0] == 0x00 or entrada_buffer[0] == 0x01:
                    continue
                
                nome = entrada_buffer[1:9].decode('utf-8').strip().lower()
                extensao = entrada_buffer[9:12].decode('utf-8').strip().lower()
                
                # Tipo definido pelo atributo (bit 1 geralmente indica arquivo)
                tipo = "arquivo" if entrada_buffer[0] == bin(2) else "diretório"

                lista_retorno.append((nome, extensao, tipo))
                    
        return lista_retorno
                    
    def listar_diretorio(self, nome):
        return

    def procurar_entrada_livre(self):
        """
        Localiza o endereço físico da primeira vaga disponível no Root Directory.
        
        :return: int: Offset absoluto (bytes) da entrada livre ou None se cheio.
        """
        offset_root_dir = self.file_sys_manager.get_offset("root_dir")
        caminho_particao = self.file_sys_manager.get_endereco_particao()
        num_entradas = self.file_sys_manager.get_num_entradas_raiz()

        with open(caminho_particao, "rb") as f:
            f.seek(offset_root_dir)

            for _ in range(num_entradas):
                posicao_atual = f.tell()
                byte_array = f.read(22)

                if byte_array[0] == 0x0: # 0x0 indica entrada que nunca foi usada
                    return posicao_atual
            return None

    def desalocar_entrada_arquivo(self, nome_arquivo : str, extensao_arquivo : str):
        """
        Realiza a exclusão lógica de um arquivo marcando o atributo como 0x01.
        
        :param nome_arquivo: str: Nome do arquivo a ser removido.
        :return: bool: True se encontrado e removido, False caso contrário.
        """
        offset_root_dir = self.file_sys_manager.get_offset("root_dir")
        caminho_particao = self.file_sys_manager.get_endereco_particao()
        num_entradas = self.file_sys_manager.get_num_entradas_raiz()

        nome_arquivo = nome_arquivo.lower()
        extensao_arquivo = extensao_arquivo.lower()

        with open(caminho_particao, "r+b") as file:
            file.seek(offset_root_dir)

            for _ in range(num_entradas):
                posicao_inicial = file.tell()
                entrada = file.read(22)

                if entrada[0] == 0x0 or entrada[0] == 0x1:
                    continue

                nome = entrada[1:9].decode('utf-8').strip().lower()
                extensao = entrada[9:12].decode('utf-8').strip().lower()

                if nome_arquivo == nome and extensao_arquivo == extensao:
                    file.seek(posicao_inicial)
                    # 0x01 marca a entrada como "excluída", permitindo reutilização
                    file.write((0x01).to_bytes(1, 'little'))
                    return True
        return False