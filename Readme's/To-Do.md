# Listagem de classes e métodos a serem desenvolvidos

## file_system_manager
### Classes feitas
```python
get_bytes_por_setor
get_setores_por_tabela
get_setores_por_cluster
get_num_entradas_raiz
get_offset
get_tamanho_cluster
ler_input_interface
disparar_comando
comando_exemplo
comando_exemplo2
comando_deletar
comando_bootrecord
comando_copiar
comando_listar
comando_mover
comando_formatar
```
### Classes faltantes
```python

```

### Testes feitos
```python
test_ler_input_interface
test_comando_formatar_caminho_invalido
test_comando_formatar_cancelado
test_comando_formatar_sucesso
```

### Testes faltantes
```python
comando_deletar
comando_bootrecord
comando_copiar
comando_listar
comando_mover
```

---------------------------------------------------------------------------------------------
## data_manager
### Classes feitas
```python
procurar_cluster_livre
alocar_cluster
```
### Classes faltantes
```python
liberar_cluster
```

### Testes feitos
```python
Nenhum
```

### Testes faltantes
```python
test_procurar_cluster_livre
test_alocar_cluster
```

---------------------------------------------------------------------------------------------
## disk_manager
### Classes feitas
```python
ler_setor
escrever_setor
```

### Classes faltantes
```python

```

### Testes feitos
```python
Nenhum
```

### Testes faltantes
```python
test_ler_setor
test_escrever_setor
```


---------------------------------------------------------------------------------------------
## FAT_table_manager
### Classes feitas
```python
get_entrada_FAT
alocar_arquivo
```

### Classes faltantes
```python
desalocar_arquivo
pegar_proximo_cluster
sincronizar_fat
```
 
### Testes feitos
```python
Nenhum
```

### Testes faltantes
```python
test_get_entrada_FAT
test_alocar_arquivo
```

---------------------------------------------------------------------------------------------
## root_dir_manager
### Classes feitas
```python
Nenhuma
```

### Classes faltantes
```python
escrever_entrada
ler_entrada
desalocar_entrada
listar_entradas
```

### Testes feitos
```python
Nenhum
```

### Testes faltantes
```python
test_root_dir_manager
```

------------------------------------------------------------------------------------------
##  Formatador

### Testes feitos
```python
teste_formatador
test_escrever_boot_record
```

### Testes faltantes
```python

```

------------------------------------------------------------------------------------------
## Interface


### Classes feitas
```python
executar
exibir
```

### Classes faltantes
```python

```