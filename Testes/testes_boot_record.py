# Arquivo para reunir os testes dos modulos
from Classes.boot_record import BootRecord
import unittest

def test_boot_record():
    boot_record = BootRecord()
    
    assert boot_record.get_bytes_por_setor() == 512, "Bytes por setor incorreto"
    assert boot_record.get_setores_por_tabela() == 131072, "Setores por tabela incorreto"
    assert boot_record.get_setores_por_cluster() == 8, "Setores por cluster incorreto"
    assert boot_record.get_num_entradas_raiz() == 512, "Número de entradas da raiz incorreto"
    
    print("Todos os testes do Boot Record passaram!")


#############################################################################################################################

if __name__ == "__main__":
    unittest.main()
test_boot_record()