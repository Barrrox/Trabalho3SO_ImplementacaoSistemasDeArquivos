from Classes.file_system_manager import FileSystemManager 

class interface:
    def __init__(self):
        self.manager = FileSystemManager()

        # comandos aceitos e número mínimo de argumentos
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
        if comando not in self.comandos:
            return False, f"[sys] - Comando ({comando}) não encontrado."

        min_args = self.comandos[comando]
        if len(args) < min_args:
            return False, f"[sys] - Uso incorreto. Esperado {min_args} argumento(s)."

        return True, None

    def executar(self):
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

            resultado = self.manager.ler_input_interface(entrada)
            self.exibir(resultado)

    def mostrar_ajuda(self):
        print("[sys] - Lista de comandos:")
        print(" -> deletar <arquivo>")
        print(" -> copiar <origem> <destino>")
        print(" -> listar")
        print(" -> bootrecord")
        print(" -> formatar <partição> <bytes/setor> <setores/cluster> <entradas raiz>")
        print(" -> quit")

    def exibir(self, resultado):
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
