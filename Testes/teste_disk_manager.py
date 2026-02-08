import unittest
import os
from Classes.file_system_manager import FileSystemManager
from Testes import TAMANHO_TESTE

class TestDiskManager(unittest.TestCase):

    def setUp(self):
        # 1. Instancia o Orquestrador
        self.fsm = FileSystemManager()
        
        # 2. Configura o arquivo de disco virtual para os testes
        self.caminho_particao = "disco_teste_disk.bin"
        self.tamanho_teste = TAMANHO_TESTE
        
        # Cria o arquivo binário zerado
        with open(self.caminho_particao, 'wb') as f:
            f.seek(self.tamanho_teste - 1)
            f.write(b'\x00')

        # 3. Formata o disco (Necessário para inicializar os parâmetros nos Managers)
        # Config: 512 bytes/setor, 8 setores/cluster, 512 entradas raiz
        self.fsm.comando_formatar(self.caminho_particao, "512", "8", "512")
        
        # Atalho para o manager testado
        self.dm = self.fsm.disk_manager

    def tearDown(self):
        # Remove o arquivo de teste após cada execução
        if os.path.exists(self.caminho_particao):
            os.remove(self.caminho_particao)

    def test_escrever_e_ler_um_setor_completo(self):
        """Testa a escrita e leitura de exatamente 512 bytes em um setor."""
        tamanho_setor = self.fsm.get_bytes_por_setor()
        dados_originais = b"D" * tamanho_setor
        posicao_teste = 0 # Início do disco (Boot Record)

        with open(self.caminho_particao, "r+b") as f:


            # Escrita
            bytes_escritos = self.dm.escrever_setor(posicao_teste, dados_originais, f)
            self.assertEqual(bytes_escritos, tamanho_setor)

            # Leitura
            dados_lidos = self.dm.ler_setor(posicao_teste, f)
            self.assertEqual(dados_lidos, dados_originais)

    def test_escrever_setor_com_padding(self):
        """Testa se a escrita completa com zeros quando os dados são menores que o setor."""
        tamanho_setor = self.fsm.get_bytes_por_setor()
        dados_curtos = b"TESTE_PADDING"
        posicao_teste = tamanho_setor * 2 # Setor 2

        with open(self.caminho_particao, "r+b") as f:

            # Execução
            self.dm.escrever_setor(posicao_teste, dados_curtos, f)

            # Validação Física
        
            f.seek(posicao_teste)
            conteudo_final = f.read(tamanho_setor)
            
            # Deve começar com os dados e terminar com zeros
            self.assertTrue(conteudo_final.startswith(dados_curtos))
            self.assertEqual(conteudo_final[len(dados_curtos):], b'\x00' * (tamanho_setor - len(dados_curtos)))

    def test_escrever_multiplos_setores(self):
        """Testa a escrita de dados que ocupam mais de um setor."""
        tamanho_setor = self.fsm.get_bytes_por_setor()
        # Dados para ocupar exatamente 2 setores
        dados_1 = b"1" * tamanho_setor
        dados_2 = b"2" * tamanho_setor
        
        posicao_teste = tamanho_setor * 10 # Setor 10

        with open(self.caminho_particao, "r+b") as f:

            # Execução
            self.dm.escrever_setor(posicao_teste, dados_1, f)
            self.dm.escrever_setor(posicao_teste+tamanho_setor, dados_2, f)

            bytes_escritos1 = self.dm.ler_setor(posicao_teste, f)
            bytes_escritos2 = self.dm.ler_setor(posicao_teste+tamanho_setor, f)

        # Deve ter escrito 1024 bytes (2 setores)
        self.assertEqual(bytes_escritos1, dados_1)
        self.assertEqual(bytes_escritos2, dados_2)

    def test_ler_setor_fora_do_inicio(self):
        """Garante que a leitura respeita o offset/posicao informada."""
        tamanho_setor = self.fsm.get_bytes_por_setor()
        dados_especificos = b"SETOR_ALVO" + (b"\x00" * (tamanho_setor - 10))
        posicao_alvo = tamanho_setor * 5 # Setor 5

        # Prepara o disco manualmente
        with open(self.caminho_particao, "r+b") as f:
            f.seek(posicao_alvo)
            f.write(dados_especificos)

            # Executa a leitura via manager
            dados_lidos = self.dm.ler_setor(posicao_alvo, f)
        self.assertEqual(dados_lidos, dados_especificos)

if __name__ == '__main__':
    unittest.main()