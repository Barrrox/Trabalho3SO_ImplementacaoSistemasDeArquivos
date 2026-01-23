# Testes em python

Esse arquivo contém infos úteis/necessárias para conseguir criar os testes em python

# Base para os testes

Em python existe a biblioteca padrão para testes chamada **unittest**. Para o unittest funcionar corretamente, precisa do seguinte:
- Nomenclatura: Métodos de teste devem começar com o prefixo test_.
- Referência: O método de teste precisa receber self.
- Classe: A classe teste precisa herdar TestCase. Exemplo:
```python
class TesteFormatador(TestCase):
```
- Usar setUp e tearDown: São métodos definidos pela classe TestCase e são executados automaticamente sem serem chamados. Precisam ser usados para inicializar e fechar o teste. 

## Rodar todos os testes

```python
python -m unittest discover -s Testes -p "teste_*.py"
```