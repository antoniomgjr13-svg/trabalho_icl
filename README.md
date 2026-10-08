# Verificador Lógico

Trabalho de Introdução aos Circuitos Lógicos (ENEL 1). Python 3, só biblioteca padrão.

## Como executar

**VS Code / terminal:** `python verificador_logico.py` (abre um menu).

**Google Colab:** cole o código numa célula e rode, ou suba o arquivo e use
`%run verificador_logico.py`. Também dá para usar as funções direto:

```python
import verificador_logico as v
v.tabela_verdade("(P e ~Q) -> R")
v.classificar("P ou ~P")              # 'tautologia'
v.equivalentes("P -> Q", "~P ou Q")   # (True, None)
v.argumento_valido(["P -> Q", "Q"], "P")   # (False, {'P': False, 'Q': True})
v.resolver(["A -> B", "A"])           # valorações que tornam tudo verdadeiro
v.apenas_um_mentiu(["P", "Q", "~P ou ~Q"])
```

## Sintaxe aceita

| Conectivo | Símbolos |
|---|---|
| Negação | `~P`, `!P`, `não P` |
| Conjunção | `P e Q`, `P ^ Q`, `P & Q` |
| Disjunção | `P ou Q`, `P v Q`, `P | Q` |
| Condicional | `P -> Q` |
| Bicondicional | `P <-> Q` |
| Ou exclusivo | `P xor Q` |

- Proposições: **uma letra maiúscula** (P, Q, R, A, B...). Operadores em minúsculas.
- Parênteses são aceitos.
- Precedência (maior → menor): `~`, `e`, `xor`, `ou`, `->`, `<->`.
  `->` associa à direita: `P -> Q -> R` = `P -> (Q -> R)`.
- Expressão inválida gera mensagem explicando o erro (parêntese faltando,
  operando faltando, caractere inválido etc.).

## Funcionalidades

1. **Tabela-verdade** com colunas intermediárias + classificação (tautologia, contradição, contingência).
2. **Equivalência** de duas sentenças e **validade de argumento** com contraexemplo.
3. **Resolução de problemas**: lista valorações que tornam as condições verdadeiras.
   Restrições extras: `apenas_um_mentiu(lista)`, `exatamente_uma_verdadeira(lista)`
   ou `resolver(lista, exatamente=k)`. Também dá para escrever a restrição como sentença.
4. **Bônus:** soma de produtos e produto de somas, cada um com o desenho do circuito lógico (NOT, AND, OR). Interface web com Streamlit (`streamlit run app_streamlit.py`).

## Exemplos

- `P ou ~P` → tautologia
- `P e ~P` → contradição
- `~(P e Q)` equivale a `~P ou ~Q`
- `P -> Q, P ⊢ Q` → válido
- `P -> Q, Q ⊢ P` → inválido; contraexemplo P=F, Q=V

Menu opção 6 roda todos os testes mínimos do enunciado.

### Exemplo de problema (Tarefa 3)

"Três pessoas falam; apenas uma mente." Modele com letras e use menu → 4 → modo 2.
