"""
Contém as funções para formatar o pendrive ou um arquivo mock (usado no desenvolvimento)
"""
import subprocess
import os

class Formatador:


    def zerar(self, caminho_particao : str, tamanho_particao):
        """
        Define se a execução será em um arquivo mock ou num pendrive no linux
        Não funciona para pendrives no Windows
        
        :param caminho_particao: caminho absoluto para a particao
        :param tamanho_particao: tamanho da particao em bytes
        
        """

        # Se o caminho da partição tem o "/dev/" então está no linux
        if caminho_particao.startswith("/dev/"):
            self.zerar_pendrive(caminho_particao, tamanho_particao)
        else:
            self.zerar_mock(caminho_particao, tamanho_particao)



    def zerar_mock(self, caminho_particao, tamanho_particao):
        """
        Zera um arquivo mock para os testes no windows
        
        :param caminho_particao: caminho absoluto para a particao
        :param tamanho_particao: tamanho da particao em bytes
        """

        with open(caminho_particao, 'wb') as f:
            f.seek(tamanho_particao - 1)
            f.write(b'\x00')

        return
    
    def zerar_pendrive(self, caminho_particao, tamanho_particao):
        """
        Zera o pendrive no linux.
        Funciona exclusivamento no /dev/<id_disco>
        
        :param caminho_particao: caminho absoluto para a particao
        :param tamanho_particao: tamanho da particao em bytes
        """

        # dd faz a copia bloco a bloco

        tamanho_bloco = 1024 * 1024
        # Calcula o total de blocos de 1 MB
        contagem_blocos = tamanho_particao // tamanho_bloco

        # dd = Disk Destroyer
        comando = [
            "dd",
            "if=/dev/zero",
            f"of={caminho_particao}",
            f"bs={tamanho_bloco}",
            f"count={contagem_blocos}",
            "status=progress"
        ]

        try:
            # No WSL/Linux, isso exige que você rode o script com sudo
            subprocess.run(comando, check=True)
            os.sync() # Força a gravação física
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar dd: {e}")

        return 

    # recebe os parametros em valor numérico, faz a tradução para binário (little-endian) na hora da escrita
    def escreve_boot_record(self, arquivo, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz):

        # escreve os parâmetros do boot record
        with open(arquivo, 'r+b') as f:

            f.seek(3)  # Pular os primeiros 3 bytes reservados
            f.write(bytes_por_setor.to_bytes(2, byteorder='little'))       # 2 bytes

            f.seek(5)  # Pular para o offset 5
            f.write(setores_por_tabela.to_bytes(4, byteorder='little'))    # 4 bytes

            f.seek(9)  # Pular para o offset 9
            f.write(setores_por_cluster.to_bytes(1, byteorder='little'))   # 1 byte

            f.seek(10) # Pular para o offset 10
            f.write(num_entradas_raiz.to_bytes(2, byteorder='little'))     # 2 bytes

        return  
        # def escreve_boot_record(self, arquivo, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz ):


    def formatar_completo(self, caminho_particao, tamanho_particao, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz):
        # formata o armazenamento completamente para FAT48
        # boot record | tabela FAT 1 | tabela FAT 2 | root dir | área de dados

        # Preenche com zeros
        self.zerar(caminho_particao, tamanho_particao) 
        
        # Escreve as inforamações no boot record
        self.escreve_boot_record(caminho_particao, bytes_por_setor, setores_por_tabela, setores_por_cluster, num_entradas_raiz)
        
        return    
