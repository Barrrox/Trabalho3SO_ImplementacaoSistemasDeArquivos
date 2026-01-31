"""
Arquivo para criar um disco virtual mock com um tamanho especificado em setores.
Usado apenas para testes e simulações.
"""

def criar_disco_mock(nome_arquivo, num_setores):
    tamanho_setor = 512
    tamanho_total = num_setores * tamanho_setor
    
    try:
        with open(nome_arquivo, "wb") as f:
            # Opção A: Escrever todos os zeros (mais lento, mas garante o espaço)
            # f.write(b'\x00' * tamanho_total)
            
            # Opção B: "Seek" até o final e escreve um byte (Rápido - cria um arquivo esparso)
            f.seek(tamanho_total - 1)
            f.write(b'\x00')
            
        print(f"Sucesso: Arquivo '{nome_arquivo}' criado com {tamanho_total} bytes.")
    except Exception as e:
        print(f"Erro ao criar o disco mock: {e}")

# Exemplo: Criar um disco de 10MB (aprox. 20.000 setores)
# criar_disco_mock("disco_virtual.bin", 20000)

