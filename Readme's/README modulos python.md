# IMPORTANTE!!!

Aqui escrevo sobre como executar os arquivos desse repositorio da maneira correta para fazer os imports funcionarem, que envolve o uso dos arquivos **__init__.py**. Vou primeiro mostrar como executávamos python antes e como devemos agora, e depois explicar o porquê disso caso queira ler.

Antes nós executaríamos assim:

```terminal
python.exe ./caminho/do/arquivo.py
```

Isso pode funcionar, mas vai dar problema se o arquivo faz imports de fora da sua pasta, como é o caso dos arquivos na pasta Testes. Como executar agora:

```terminal
python.exe -m caminho.do.arquivo 
```

## Explicação

Para que um arquivo importe conteúdo de arquivos fora da sua pasta, ele tem duas opções:
1. utilzar o módulo sys, que envolveria adicionar o path do arquivo desejado dentro do arquivo importador toda vez, o que é totalmente anti-engenharia de software.
2. transformar as pastas em módulos python

Para transformar as pastas em módulos python, é apenas necessário criar um arquivo __init__.py vazio em cada pasta. Isso já é suficiente para o python identificar a pasta como um módulo.

Por conta dessa mudança, para executar os códigos precisamos usar o parametro **-m** e representar diretorios usando **.** em vez de **/**, além de retirar o .py do final