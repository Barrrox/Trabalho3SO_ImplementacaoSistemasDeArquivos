import math

def Perda(ArmazenamentoTotalGB, BitsFAT, BytesPorSetor, SetorPorCluster):
    """
    Calcula a perda total de espaço (em bytes) em um sistema de arquivos FAT
    devido a:
    1. Espaço não utilizado na tabela FAT (endereços além dos clusters possíveis).
    2. Espaço vazio no final da área de dados (clusters não utilizados/endereçáveis).

    Parâmetros:
    -----------
    ArmazenamentoTotalGB : float
        Capacidade total de armazenamento do volume em Gigabytes (GB).
    BitsFAT : int
        Número de bits usados para endereçar um cluster na Tabela de Alocação de Arquivos (FAT).
        Ex: 12, 16, 32.
    BytesPorSetor : int
        Tamanho de um setor em bytes.
    SetorPorCluster : int
        Número de setores que compõem um cluster.

    Retorna:
    --------
    float
        A perda total de espaço em bytes.
    """

    # Número de setores reservados para o Boot Record e Root Directory (valores comuns)
    SetoresBootRecord = 1
    SetoresRootDir = 22

    # --- Cálculo do Tamanho da FAT ---

    # O tamanho de uma única tabela FAT em bytes (2^BitsFAT entradas, cada uma com BitsFAT/8 bytes)
    TamanhoFAT_Bytes = math.ceil((2**BitsFAT) * (BitsFAT / 8))

    # O sistema FAT usa duas cópias da tabela FAT (por redundância). O tamanho total em setores.
    # math.ceil é usado pois o espaço da FAT deve ocupar um número inteiro de setores,
    # arredondando para cima.
    SetoresFAT = math.ceil(TamanhoFAT_Bytes / BytesPorSetor)

    # --- Cálculo do Tamanho da Área de Dados ---

    # Armazenamento total em bytes / Bytes por setor = Total de setores
    TotalSetores = ArmazenamentoTotalGB * (1024**3) / BytesPorSetor
    
    # Número de setores que sobraram para a área de dados após subtrair as áreas reservadas.
    # math.floor é usado para garantir um número inteiro de setores na área de dados, truncando.
    SetoresDados = math.floor(TotalSetores - (SetoresBootRecord + SetoresRootDir + 2 * SetoresFAT))
    
    # --- Perda 1: Espaço Não Utilizado na Tabela FAT ---

    # Número de clusters que a FAT pode endereçar (entradas possíveis)
    NumClusterEnderecaveis = 2**BitsFAT

    # Número de clusters fisicamente possíveis na área de dados
    NumClustersPossiveis = math.floor(SetoresDados / SetorPorCluster)

    # Endereços na FAT que não corresponderão a um cluster real (ocorre se NumClusterEnderecaveis > NumClustersPossiveis)
    EnderecosNaoUtilizadosFAT = NumClusterEnderecaveis - NumClustersPossiveis

    # Tamanho do endereço na FAT em bytes
    TamanhoEnderecoFAT = BitsFAT / 8
    # Perda em bytes na Tabela FAT devido a endereços sem clusters correspondentes.
    # Se EnderecosNaoUtilizadosFAT for negativo, significa que a perda é 0 (a FAT é menor que a área de dados).
    BytesNaoUtilizadosFAT = max(0, EnderecosNaoUtilizadosFAT * TamanhoEnderecoFAT)

    # --- Perda 2: Espaço Vazio no Final da Área de Dados ---

    # Clusters físicos que não são endereçáveis pela FAT (ocorre se NumClustersPossiveis > NumClusterEnderecaveis)
    NumClusterNaoUtilizadosDados = NumClustersPossiveis - NumClusterEnderecaveis

    # Se a diferença for negativa, a perda é 0 (todos os clusters possíveis são endereçáveis).
    NumClusterNaoUtilizadosDados = max(0, NumClusterNaoUtilizadosDados)

    # Perda em bytes na Área de Dados devido a clusters não endereçados.
    EspacoVazioDados = NumClusterNaoUtilizadosDados * SetorPorCluster * BytesPorSetor

    # Perda total em bytes
    Perda = BytesNaoUtilizadosFAT + EspacoVazioDados

    return Perda


def main():

    # --- Parâmetros de Teste ---
    ArmazenamentoTotalGB = 16

    # Testa todas as possibilidades para quantidade de bits da FAT entre 1 e 64
    # BitsFAT_possiveis = [i for i in range(1,32)]
    BitsFAT_possiveis = [24]

    # Testa todas as possibilidades entre 128 (2^7) até 8192 (2^13) bytes por setor
    # BytesPorSetor_possiveis = [2**i for i in range(1,13)]
    BytesPorSetor_possiveis = [512]
    
    # Testa todas as possibilidades entre 1 até 16 setores por cluster
    SetorPorCluster_possiveis = [i for i in range(1,50)]
    # SetorPorCluster_possiveis = [i for i in range(1,8)]

    
    
    menor_perda = float('inf')  # Inicializa com infinito para garantir que o primeiro valor será menor
    parametros_menor_perda = []

    for BitsFAT in BitsFAT_possiveis:
        for BytesPorSetor in BytesPorSetor_possiveis:
            for SetorPorCluster in SetorPorCluster_possiveis:
                
                perda_atual = Perda(ArmazenamentoTotalGB, BitsFAT, BytesPorSetor, SetorPorCluster)

                if perda_atual < menor_perda:
                    menor_perda = perda_atual
                    parametros_menor_perda = [ArmazenamentoTotalGB, BitsFAT, BytesPorSetor, SetorPorCluster]

    
    print(f"A menor perda para um armazenamento total de {parametros_menor_perda[0]} GB foi de {menor_perda} bytes\n")
    print("Parâmetros:")
    print(f"  bits para FAT: {parametros_menor_perda[1]}")
    print(f"  Bytes por setor: {parametros_menor_perda[2]}")
    print(f"  Setores por cluster: {parametros_menor_perda[3]}")

if __name__ == "__main__":
    main()