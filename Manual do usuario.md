# Manual do Usuário - Sistema de Arquivos FAT48

## 1. Visão Geral
O sistema FAT48 é um gerenciador de arquivos baseado na tabela de alocação FAT32, operando sobre dispositivos de armazenamento físico (pendrives). O sistema utiliza alocação encadeada e mantém metadados em um diretório raiz.

**Nota Importante:** O sistema não possui persistência de montagem entre execuções. É necessário formatar o dispositivo a cada nova inicialização do programa.

---

## 2. Inicialização e Formatação
Ao iniciar a aplicação, o dispositivo não está pronto para uso imediato. O primeiro comando obrigatório é a formatação para criar as estruturas de dados (Boot Record, FATs e Diretório Raiz).

**Sintaxe:**
```bash
formatar <caminho_dispositivo> <bytes_por_setor> <setores_por_cluster> <entradas_raiz>
```

## Parâmetros:

- <caminho_dispositivo>: Caminho absoluto para a partição do pendrive (ex: /dev/sdb1).

- <bytes_por_setor>: Quantidade de bytes por setor físico. (Padrão: 512).

- <setores_por_cluster>: Número de setores agrupados em um cluster. (Padrão: 8).

- <entradas_raiz>: Limite de arquivos que podem ser criados no diretório raiz. (Padrão: 512).

Exemplo de Uso:

```Bash
formatar /dev/sdb1 512 8 512
```

*Acompanhe a barra de progresso. A operação limpa todos os dados anteriores do dispositivo.*

## 3. Regras de Nomenclatura (Padrão 8.3)
O sistema utiliza uma estrutura rígida de nomes. Violações nestas regras impedem a gravação do arquivo:

* **Nome do Arquivo**: Máximo de 8 caracteres.
* **Extensão**: Máximo de 3 caracteres.
* **Caracteres**: Não utilize espaços, acentos ou caracteres especiais.
* **Case Sensitivity**: O sistema não diferencia maiúsculas de minúsculas; todos os nomes são convertidos para minúsculo internamente.

| Arquivo Válido | Arquivo Inválido | Motivo |
| :--- | :--- | :--- |
| `dados.txt` | `meu arquivo.txt` | Contém espaço |
| `imagem.png` | `foto_ferias.jpeg` | Nome > 8 e Extensão > 3 |

---

## 4. Transferência de Arquivos
O comando `copiar` é utilizado para copiar dados entre o computador host e o pendrive.

### 4.1. Importar (PC -> Pendrive)
Copia um arquivo do seu computador no pendrive formatado em FAT48.
**Sintaxe:**
```bash
copiar <caminho_origem_pc>
```

Exemplo: ```copiar C:\arquivos\projeto.zip``` 

### 4.2. Exportar (Pendrive -> PC)
Copia um arquivo de dentro do pendrive para uma pasta no seu computador. Deve ser colocado o nome e extensão do arquivo dentro do sistema FAT48.

**Sintaxe:**
```bash
copiar <nome_arquivo_no_pendrive> <caminho_destino_pc>
```

Exemplo: ```copiar projeto.zip D:\recuperado.zip```

## 5. Gerenciamento de Arquivos

### Listar Conteúdo
Exibe todos os arquivos armazenados no diretório raiz.
```bash
listar
```

**Deletar Arquivo**
Remove o arquivo selecionado e libera seus clusters na tabela de alocação (FAT).

```Bash
deletar <nome.ext>
```
Exemplo: ```deletar texto.txt```

**Consultar Geometria**
Exibe os metadados técnicos (Boot Record) definidos durante a formatação.

```Bash
bootrecord
```
## 6. Limitações Técnicas Conhecidas
Para garantir o uso correto, observe as seguintes restrições do sistema FAT48:

- Estrutura Plana: Não há suporte para diretórios ou subpastas. Todos os arquivos residem obrigatoriamente na raiz.

- Capacidade por Arquivo: Um único arquivo não pode exceder o tamanho de 4 GB.

- Memória RAM: O processo de cópia exige que o computador host possua memória RAM disponível proporcional ao tamanho do arquivo sendo importado.

- Tamanho do Dispositivo: O pendrive (ou partição física) deve possuir, no mínimo, 1 MB de espaço total para o funcionamento das estruturas do sistema.

- Quantidade de Arquivos: O sistema é limitado ao número de entradas definido na raiz durante a formatação (padrão 512), independentemente do espaço disponível em bytes.

- Persistência: O sistema deve ser formatado a cada nova execução; não há suporte para leitura de partições FAT48 criadas em sessões anteriores.