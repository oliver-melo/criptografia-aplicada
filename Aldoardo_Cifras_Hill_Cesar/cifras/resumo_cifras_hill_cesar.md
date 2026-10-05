# Resumo dos métodos de cifragem: César e Hill

## Introdução

As cifras de César e de Hill são métodos de criptografia clássica usados para
transformar uma mensagem legível em um texto cifrado. Ambas têm finalidade
principalmente educacional atualmente, pois não oferecem segurança suficiente
para proteger dados reais contra computadores modernos.

## Cifra de César

A Cifra de César é um método de substituição no qual cada letra é deslocada por
uma quantidade fixa de posições no alfabeto. O número de posições escolhido é a
chave da cifra.

No código desenvolvido, a função `cifrar_cesar` avança cada letra pelo número de
posições informado. Para decifrar, a função `decifrar_cesar` realiza o mesmo
processo com um deslocamento negativo, fazendo as letras voltarem às posições
originais.

Por exemplo, com deslocamento 3:

```text
A → D
B → E
X → A

Ataque Amanha → Dwdtxh Dpdqkd
```

O cálculo usa módulo 26, pois o alfabeto utilizado contém 26 letras. Dessa
forma, depois de `Z`, o deslocamento continua novamente a partir de `A`. A
implementação preserva letras maiúsculas e minúsculas, além de manter espaços,
números e sinais de pontuação sem alterações.

A Cifra de César é simples de entender e implementar, mas também é fácil de
quebrar, porque existem poucas chaves possíveis e todas podem ser testadas
rapidamente.

## Cifra de Hill

A Cifra de Hill utiliza álgebra linear e uma matriz numérica como chave. Cada
letra é convertida em um número conforme a correspondência:

```text
A = 0, B = 1, C = 2, ..., Z = 25
```

Depois, a mensagem é dividida em blocos. O tamanho de cada bloco é determinado
pela dimensão da matriz-chave. Uma matriz 2 × 2 trabalha com blocos de duas
letras; uma matriz 3 × 3 trabalha com blocos de três letras.

Na implementação foi utilizada como exemplo a matriz:

```text
| 3  3 |
| 2  5 |
```

Em Python, essa matriz é representada por:

```python
chave = [[3, 3], [2, 5]]
```

Cada bloco da mensagem é transformado em um vetor e multiplicado pela
matriz-chave. Os resultados são calculados no módulo 26 e convertidos novamente
em letras. Com essa chave, por exemplo:

```text
PARA → PA | RA → TE | ZI → TEZI
```

Para decifrar, o código calcula a inversa modular da matriz-chave e a aplica aos
blocos do texto cifrado:

```text
TEZI → PARA
```

A matriz precisa ser quadrada e invertível no módulo 26. Para isso, o máximo
divisor comum entre o determinante da matriz e 26 deve ser igual a 1. Se essa
condição não for atendida, a mensagem não poderá ser recuperada corretamente e
o programa rejeitará a chave.

Antes da cifragem, a implementação da Cifra de Hill:

- converte todas as letras para maiúsculas;
- remove os acentos;
- remove espaços, números e sinais de pontuação;
- adiciona a letra `X` quando o último bloco está incompleto.

Por exemplo, usando uma matriz 2 × 2, `AJUDA` possui cinco letras e precisa ser
completada:

```text
AJUDA → AJ | UD | AX
```

Por esse motivo, o resultado da decifragem pode ser `AJUDAX`. Nesse caso, o `X`
final é apenas um caractere de preenchimento.

## Comparação entre os métodos

A Cifra de César modifica uma letra por vez usando sempre o mesmo deslocamento.
Ela é mais simples, preserva a formatação da mensagem e exige apenas um número
como chave.

A Cifra de Hill transforma várias letras ao mesmo tempo e usa uma matriz como
chave. Por misturar as letras de cada bloco, seu funcionamento é mais complexo e
esconde melhor os padrões individuais das letras. Entretanto, assim como a
Cifra de César, a Cifra de Hill é considerada insegura para aplicações modernas.

## Conclusão

Os dois métodos ajudam a compreender conceitos fundamentais da criptografia. A
Cifra de César demonstra substituição e aritmética modular, enquanto a Cifra de
Hill acrescenta operações com matrizes, determinantes e inversos modulares. O
código desenvolvido permite cifrar e decifrar mensagens com ambos os métodos,
além de validar a matriz usada na Cifra de Hill.
