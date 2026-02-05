import unittest
import os
import sys
from Formatador.formatador import Formatador

"""
Se quiser testar no pendrive altere CAMINHO_ALVO para "/dev/<id_pendrive>"
id_pendrive pode ser descoberto com o comando "usbipd list" no linux

O teste no pendrive demora dependendo do tamanho. Uma partição de 1GB demorou 1 min 
quando eu (Barros) testei

"""
CAMINHO_ALVO = "disco_teste_formatador.bin" 

class TesteZerar(unittest.TestCase):

    def setUp(self):
        self.formatador = Formatador()
        self.caminho_teste = CAMINHO_ALVO
        
        # Se for hardware, detectamos o tamanho real. Se for mock, definimos 10MB.
        if self.caminho_teste.startswith("/dev/"):
            if not os.path.exists(self.caminho_teste):
                self.skipTest(f"Dispositivo {self.caminho_teste} não encontrado.")
            
            with open(self.caminho_teste, 'rb') as f:
                self.tamanho_teste = f.seek(0, os.SEEK_END)
            
            # Suja apenas o início para validar a limpeza sem demorar
            with open(self.caminho_teste, "r+b") as f:
                f.write(b"A" * 1024 * 1024) # 1MB de lixo
        else:
            self.tamanho_teste = 1024 * 1024 * 10 # 10 MB
            with open(self.caminho_teste, "wb") as f:
                f.write(b"A" * self.tamanho_teste)

    def tearDown(self):
        # Só remove se for um arquivo comum (mock)
        if os.path.exists(self.caminho_teste) and not self.caminho_teste.startswith("/dev/"):
            os.remove(self.caminho_teste)

    def test_zerar_hibrido(self):
        # O formatador decide internamente se usa dd ou python
        self.formatador.zerar(self.caminho_teste, self.tamanho_teste)

        # Validação robusta: lê em blocos para suportar pendrives grandes sem MemoryError
        chunk_size = 1024 * 1024 # 1MB
        bytes_verificados = 0
        # No pendrive, verificamos apenas os primeiros 10MB por performance
        limite_verificacao = min(self.tamanho_teste, 1024 * 1024 * 10)

        with open(self.caminho_teste, "rb") as f:
            while bytes_verificados < limite_verificacao:
                chunk = f.read(chunk_size)
                if not chunk: break
                self.assertTrue(all(byte == 0 for byte in chunk), f"Erro: bytes não-zero no offset {bytes_verificados}")
                bytes_verificados += len(chunk)

class TesteEscreverBootRecord(unittest.TestCase):

    def setUp(self):
        self.caminho_teste = CAMINHO_ALVO
        self.formatador = Formatador()
        
        if not self.caminho_teste.startswith("/dev/"):
            self.tamanho_disco = 2048
            self.formatador.zerar(self.caminho_teste, self.tamanho_disco)
        else:
            # No hardware, apenas garantimos que o setor 0 está limpo antes do teste
            with open(self.caminho_teste, "r+b") as f:
                f.write(b"\x00" * 512)

    def tearDown(self):

        # Se não é o pendrive, ban no arquivo
        if not self.caminho_teste.startswith("/dev/") and os.path.exists(self.caminho_teste) :
            os.remove(self.caminho_teste)

    def test_escrever_boot_record(self):
        cenarios = [(512, 512, 8, 512)]

        for b_setor, s_tabela, s_cluster, n_raiz in cenarios:
            self.formatador.escreve_boot_record(self.caminho_teste, b_setor, s_tabela, s_cluster, n_raiz)

            with open(self.caminho_teste, "rb") as f:
                setor_0 = f.read(512)

            self.assertEqual(int.from_bytes(setor_0[3:5], 'little'), b_setor)
            self.assertEqual(int.from_bytes(setor_0[5:9], 'little'), s_tabela)
            self.assertEqual(int.from_bytes(setor_0[10:12], 'little'), n_raiz)

if __name__ == "__main__":
    unittest.main()