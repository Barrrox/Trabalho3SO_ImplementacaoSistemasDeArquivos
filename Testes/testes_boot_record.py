"""
Testa se a escrita do boot record está funcionando. O teste escreve em um 
arquivo binário gerado apenas para esse código e lê logo depois para verificar
se foi escrito corretamente
"""


from Formatador.formatador import formatador
import os
import unittest

class TesteBootRecord(unittest.TestCase):

    def setUp(self):
        self.caminho_teste = "disco_teste_boot_record.bin"
        self.tamanho_disco = 2048 # 2Kb so pra testar
        formatador.zerar(self.caminho_teste, self.tamanho_disco)
        self.formatador = formatador()

    def tearDown(self):
        if os.path.exists(self.caminho_teste):
            # os.remove(self.caminho_teste)
            print("YUP!")

    def test_escrever_boot_record(self):
        """Testa a escrita com múltiplos cenários de entrada do usuário"""

        # Lista de cenários: (bytes_setor, setores_tabela ,setores_cluster, n_raiz)
        cenarios = [
            (512, 512, 8, 512),    # Cenário Padrão
            (1024, 256, 4, 1024),  # Cenário Setor Grande
            (256, 1638400, 1, 256),  # Cenário Tabela Grande
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