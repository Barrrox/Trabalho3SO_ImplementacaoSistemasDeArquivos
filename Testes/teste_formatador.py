import unittest
import os

from Formatador.formatador import Formatador

class TesteZerar(unittest.TestCase):

    # setUp é pedido pela classe TestCase para realizar o testes
    def setUp(self):
        """
        Não podemos fazer o teste na partição real, pois se a partição já estiver cheia
        de zeros, não estariamos testando realmente se a função está funcionando. 
        Então criamos um arquivo mock para simular a partição que será excluido depois
        """

        self.formatador = Formatador()
        self.caminho_teste = "disco_teste_zerar.bin"
        self.tamanho_teste = 1024 * 1024 * 10 # 10 MB

        with open(self.caminho_teste, "wb") as f:
            f.write(b"A" * self.tamanho_teste) # Escrever dados aleatorios

    # tearDown é pedido pela classe TestCase para realizar o teste
    def tearDown(self):
        if os.path.exists(self.caminho_teste):
            os.remove(self.caminho_teste)

    def test_zerar(self):

        # chama a função para testar
        self.formatador.zerar(self.caminho_teste, self.tamanho_teste)

        # Verifica se tem o mesmo tamamnho
        tamanho_real = os.path.getsize(self.caminho_teste)
        
        assert tamanho_real == self.tamanho_teste
        
        # abre o conteudo
        with open(self.caminho_teste, "rb") as f:
            dados = f.read()

        # all retorna true se for tudo zero
        eh_tudo_zero = all(byte == 0 for byte in dados)

        assert eh_tudo_zero == True

class TesteEscreverBootRecord(unittest.TestCase):

    def setUp(self):
        self.caminho_teste = "disco_teste_escrever_boot_record.bin"
        self.tamanho_disco = 2048 # 2Kb so pra testar
        self.formatador = Formatador()
        self.formatador.zerar(self.caminho_teste, self.tamanho_disco)


    def tearDown(self):
        if os.path.exists(self.caminho_teste):
            os.remove(self.caminho_teste)

    def test_escrever_boot_record(self):
        """Testa a escrita com múltiplos cenários de entrada do usuário"""

        # Lista de cenários: (bytes_setor, setores_tabela ,setores_cluster, n_raiz)
        cenarios = [
            (512, 512, 8, 512),    # Cenário Padrão
            (1024, 256, 4, 1024),  # Cenário Setor Grande
            (256, 16384, 1, 256),  # Cenário Tabela Grande
        ]

        for bytes_setor, setores_tabela ,setores_cluster, n_raiz  in cenarios:

            # 1. Escreve
            self.formatador.escreve_boot_record(self.caminho_teste, bytes_setor, setores_tabela, setores_cluster, n_raiz)

            # 2. Le o que acabou de escrever
            with open(self.caminho_teste, "rb") as f:
                setor_0 = f.read(512)

            # 3. Valida
            # Offset 0x03 - 2 bytes
            lido_setor = int.from_bytes(setor_0[3:5], 'little')
            self.assertEqual(lido_setor, bytes_setor)

            # Offset 0x05 - 4 bytes
            lido_tabela = int.from_bytes(setor_0[5:9], 'little')
            self.assertEqual(lido_tabela, setores_tabela)

            # Offset 0x09 - 1 byte
            lido_cluster = int.from_bytes(setor_0[9:10], 'little')
            self.assertEqual(lido_cluster, setores_cluster)

            # Offset 0x0A - 2 bytes
            lido_raiz = int.from_bytes(setor_0[10:12], 'little')
            self.assertEqual(lido_raiz, n_raiz)

if __name__ == "__main__":
    unittest.main()
