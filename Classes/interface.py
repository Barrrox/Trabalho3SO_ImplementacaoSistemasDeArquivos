from Classes.file_system_manager import FileSystemManager 

class interface:
    """
    Interface de Linha de Comando (CLI) para interação com o sistema de arquivos.
    Atua como mediador entre as entradas do utilizador e o FileSystemManager.
    """
    def __init__(self):
        """
        Inicializa o gestor do sistema e define os comandos suportados.
        """
        self.manager = FileSystemManager()

        # Comandos aceites e o respetivo número mínimo de argumentos exigidos
        self.comandos = {
            "deletar": 1,
            "copiar": 1,
            "listar": 0,
            "bootrecord": 0,
            "formatar": 4,
            "exemplo": 2,
            "exemplo2": 0
        }

    def checagem(self, comando, args):
        """
        Valida se o comando existe e se a quantidade de argumentos é suficiente.
        
        :param comando: str: Nome do comando a validar.
        :param args: list: Lista de argumentos fornecidos.
        :return: (bool, str): Tuplo com estado da validação e mensagem de erro se necessário.
        """
        if comando not in self.comandos:
            return False, f"[sys] - Comando ({comando}) não encontrado."

        min_args = self.comandos[comando]
        if len(args) < min_args:
            return False, f"[sys] - Uso incorreto. Esperado {min_args} argumento(s)."

        return True, None

    def executar(self):
        """
        Loop principal da interface que processa comandos até ao encerramento (quit).
        """
        print("[sys] Sistema de Arquivos iniciado. Digite 'ajuda'.")

        while True:
            entrada = input("\n>> ").strip()

            if not entrada:
                continue

            partes = entrada.split()
            comando = partes[0]
            args = partes[1:]

            if comando == "quit":
                print("[sys] Encerrando sistema...")
                break

            if comando == "ajuda":
                self.mostrar_ajuda()
                continue

            valido, erro = self.checagem(comando, args)
            if not valido:
                print(erro)
                continue

            # Processa o input através do gestor do sistema de arquivos
            resultado = self.manager.ler_input_interface(entrada)
            self.exibir(resultado)

    def mostrar_ajuda(self):
        """
        Lista todos os comandos disponíveis e os seus parâmetros.
        """
        print("[sys] - Lista de comandos:")
        print(" -> deletar <arquivo>")
        print(" -> copiar <origem> <destino>")
        print(" -> listar")
        print(" -> bootrecord")
        print(" -> formatar <partição> <bytes/setor> <setores/cluster> <entradas raiz>")
        print(" -> quit")

    def exibir(self, resultado):
        """
        Imprime o resultado dos comandos formatado conforme o tipo de dado retornado.
        
        :param resultado: list/dict/str: Objeto retornado pelo manager.
        """
        if resultado is None:
            return

        if isinstance(resultado, list):
            for linha in resultado:
                print(linha)

        elif isinstance(resultado, dict):
            for chave, valor in resultado.items():
                print(f"{chave}: {valor}")

        else:
            print(resultado)