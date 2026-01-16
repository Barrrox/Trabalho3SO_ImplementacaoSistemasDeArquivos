import unittest
import os

from Formatador.formatador import formatador

class TesteFormatador(unittest.TestCase):

    # setUp é pedido pela classe TestCase para realizar o testes
    def setUp(self):
        """
        Não podemos fazer o teste na partição real, pois se a partição já estiver cheia
        de zeros, não estariamos testando realmente se a função está funcionando. 
        Então criamos um arquivo mock para simular a partição que será excluido depois
        """
        self.formatador = formatador
        self.caminho_teste = "disco_teste.bin"
        self.tamanho_teste = 1024 * 1024 # 1 MB

        with open(self.caminho_teste, "wb") as f:
            f.write(b"A" * self.tamanho_teste) # Escrever dados aleatorios

    # tearDown é pedido pela classe TestCase para realizar o teste
    def tearDown(self):
        if os.path.exists(self.caminho_teste):
            os.remove(self.caminho_teste)

    def test_zerar(self):

        # chama a função para testar
        formatador.zerar(self.caminho_teste, self.tamanho_teste)

        # Verifica se tem o mesmo tamamnho
        tamanho_real = os.path.getsize(self.caminho_teste)
        
        assert tamanho_real == self.tamanho_teste
        
        # abre o conteudo
        with open(self.caminho_teste, "rb") as f:
            dados = f.read()

        # all retorna true se for tudo zero
        eh_tudo_zero = all(byte == 0 for byte in dados)

        assert eh_tudo_zero == True

if __name__ == "__main__":
    unittest.main()
