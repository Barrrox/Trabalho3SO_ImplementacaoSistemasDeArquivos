"""
Arquivo para criar um disco virtual mock com um tamanho especificado em setores.
Usado apenas para testes e simulações.
"""

def criar_disco_mock(nome_arquivo, tamanho_total = None):
    tamanho_setor = 512
    
    try:
        with open(nome_arquivo, "wb") as f:
            f.seek(tamanho_total - 1)
            f.write(b'\x00')
                            
    except Exception as e:
        print(f"Erro ao criar o disco mock: {e}")

# Exemplo: Criar um disco de 1GB

criar_disco_mock("disco_virtual.bin", 1024 * 1024 * 1024)

