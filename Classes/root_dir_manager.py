
class root_dir_manager:

    def __init__(self, file_sys_manager):

        self.file_sys_manager = file_sys_manager



    def escrever_entrada(atributo, nome, extensao, tamanho, dono, nivel_de_acesso, primeiro_cluster):        
        
        # verificar se nome.extensao já existe
        # 
        
        return

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