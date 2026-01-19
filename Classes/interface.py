from Classes.file_system_manager import FileSystemManager

class interface:
    # cria objeto file_system_manager para ser usado na interface
    def __init__(self):
        self.manager = FileSystemManager()
    
    def executar(self):
        while(True): # espera por comando
            comando = input(">> ")
            
            if comando.lower() == "quit": # sai do programa 
                break
            
            else:
                resultado = self.manager.ler_input_interface(comando) # executa o comando no file_system_manager
                self.exibir(resultado)
        
    def exibir(self, resultado):
        for i in resultado:
            print(i)

                
    
        






