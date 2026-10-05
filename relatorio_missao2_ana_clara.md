# Missão 2 — Cifras Clássicas e de Fluxo

**Autora:** Ana Clara Nery e Mello Figueiredo
**Funções implementadas:** Cifra de função Afim, Cifra de Vigenère, Cifra de Fluxo (LFSR)
**Arquivos:** `src/cifras_classicas.py`, `src/cifra_fluxo.py`, `src/_t_cifras_classicas.py`, `src/_t_cifra_fluxo.py`

---

## 1. Cifra de função Afim

### Método

A cifra afim é uma substituição monoalfabética que trata o alfabeto como o conjunto Z_m, onde m é o número de letras (26, no alfabeto latino). Cada letra é convertida no seu índice e transformada por uma função linear:

```
Cifragem:   E(x) = (a·x + b) mod m
Decifragem: D(y) = a⁻¹·(y − b) mod m
```

A chave é o par (a, b). O parâmetro `b` é um deslocamento simples; o parâmetro `a` é um fator multiplicativo e é ele que distingue a cifra afim da cifra de César que é, na verdade, o caso particular a = 1.

### Condição de reversibilidade

A chave `a` precisa ser coprima com m. Isso não é convenção: é o que garante que E seja bijetora. Se mdc(a, m) = d > 1, a função passa a mapear m/d letras distintas no mesmo resultado e a mensagem se torna indecifrável. Com m = 26, valores como a = 2 ou a = 13 são proibidos.

A decifragem depende do **inverso multiplicativo** de `a` módulo m, que só existe sob essa mesma condição. A implementação o obtém pelo algoritmo estendido de Euclides, reaproveitando `NumeroModular.inverso_multiplicativo()` da Missão 1.

### Espaço de chaves

A quantidade de valores válidos para `a` é exatamente φ(m), a função totiente de Euler, implementada na Missão 1. Para m = 26:

```
φ(26) · 26 = 12 · 26 = 312 chaves possíveis
```

### Vulnerabilidades

1. **Força bruta.** 312 chaves são varridas em milissegundos. A função `forca_bruta_afim()` devolve todas as decifragens possíveis; o texto correto é identificável a olho nu.
2. **Análise de frequência.** Por ser monoalfabética, a cifra preserva a distribuição estatística do idioma: a letra mais frequente do criptograma corresponde à mais frequente do português. Duas letras identificadas bastam para resolver o sistema linear e recuperar (a, b).
3. **Índice de coincidência inalterado.** Os testes mostram que o IC do texto cifrado é idêntico ao do texto claro (≈ 0,078), porque a cifra apenas permuta símbolos sem alterar suas frequências relativas.

### Decisões de implementação

- Acentuação é normalizada antes da cifragem (`ç` → `C`, `ã` → `A`), já que o alfabeto tem 26 símbolos e o português tem mais.
- Caracteres fora do alfabeto (espaços, pontuação, dígitos) atravessam sem cifrar. A alternativa seria removê-los, o que aumentaria a segurança ao esconder o tamanho das palavras, mas prejudicaria a leitura em uma demonstração didática.
- Toda a aritmética é delegada a `NumeroModular`, em vez de reimplementar `%` localmente.

---

## 2. Cifra de Vigenère

### Método

Vigenère é uma substituição **polialfabética**: uma chave de t letras define t deslocamentos diferentes, aplicados ciclicamente conforme a posição do caractere.

```
Cifragem:   E(xᵢ) = (xᵢ + k_(i mod t)) mod m
Decifragem: D(yᵢ) = (yᵢ − k_(i mod t)) mod m
```

O ganho sobre a cifra afim é direto: uma mesma letra do texto claro produz letras diferentes conforme a posição em que aparece. Nos testes, `AAAAA` cifrado com a chave `CHAVE` resulta em `CHAVE`, enquanto a cifra afim devolve `IIIII`. Isso quebra a análise de frequência simples que derruba as cifras monoalfabéticas.

Com chave de uma única letra, Vigenère degenera na cifra de César, os testes verificam essa equivalência.

### Espaço de chaves

26^t para uma chave de t letras. Para t = 10, são cerca de 1,4 × 10¹⁴ chaves: força bruta direta é inviável. A fragilidade da cifra, portanto, **não está no tamanho do espaço de chaves**, e sim na estrutura periódica.

### Vulnerabilidades

1. **Periodicidade.** A chave se repete a cada t caracteres, o que divide o criptograma em t subsequências, cada uma cifrada por um César diferente. Resolvido t, o problema vira t cifras de César independentes, triviais de quebrar.
2. **Índice de coincidência (teste de Friedman).** O IC mede a probabilidade de duas letras sorteadas ao acaso serem iguais: ≈ 0,072 em português, ≈ 0,038 em texto aleatório. Fatiando o criptograma de t em t posições, o IC médio das fatias volta ao valor do idioma quando t acerta o tamanho da chave. A função `estimar_tamanho_chave()` implementa esse ataque e recupera o tamanho correto nos testes, sem conhecimento da chave.
3. **Exame de Kasiski.** Trechos repetidos no texto claro que caiam alinhados com a chave produzem repetições no criptograma; a distância entre elas é múltipla do tamanho da chave.
4. **Reúso de chave** entre mensagens permite correlacioná-las.

A cifra só é teoricamente inquebrável no caso-limite em que a chave é aleatória, do mesmo tamanho da mensagem e nunca reutilizada, ou seja, quando deixa de ser Vigenère e vira one-time pad.

### Decisões de implementação

- O índice da chave avança **apenas** quando um caractere é efetivamente cifrado. Espaços e pontuação não consomem letras da chave, o que mantém cifragem e decifragem alinhadas.
- Cifragem e decifragem compartilham o mesmo núcleo, com um parâmetro de sinal (+1 / −1), evitando código duplicado.

---

## 3. Cifra de Fluxo (Linear Feedback Shift Register)

### Método

Cifras de fluxo não substituem símbolos de um alfabeto: geram uma sequência pseudoaleatória de bits (o *keystream*) e a combinam com o texto claro por XOR, bit a bit.

```
c = p ⊕ k        p = c ⊕ k
```

Como o XOR é sua própria inversa, cifrar e decifrar são a **mesma operação**, os testes verificam que `cifrar(cifrar(x)) == x`.

O gerador usado é um LFSR na configuração de Fibonacci. O estado é um registrador de n bits e, a cada passo:

1. o bit menos significativo sai como bit do keystream;
2. os bits nas posições de realimentação são combinados por XOR;
3. o registrador desloca uma posição e o bit de realimentação entra no topo.

As posições de realimentação vêm de um **polinômio sobre GF(2)**. A implementação recebe esse polinômio como a lista dos seus expoentes: `[16, 14, 13, 11]` representa x¹⁶ + x¹⁴ + x¹³ + x¹¹ + 1, e mapeia cada expoente c ao bit de índice (n − c).

### Período

Se o polinômio for **primitivo**, o registrador percorre todos os 2ⁿ − 1 estados não nulos antes de repetir. Os testes confirmam:

| Registrador | Polinômio | Período medido | Máximo teórico |
|---|---|---|---|
| 4 bits | x⁴ + x³ + 1 | 15 | 2⁴ − 1 = 15 |
| 16 bits | x¹⁶ + x¹⁴ + x¹³ + x¹¹ + 1 | 65.535 | 2¹⁶ − 1 = 65.535 |

Um polinômio não primitivo encurta drasticamente o período. Durante o desenvolvimento, uma convenção errada de mapeamento dos expoentes produziu um período de apenas 3 bits em um registrador de 4, o keystream passava a ser `110110110...`, inútil como máscara.

### Vulnerabilidades

1. **Linearidade.** Esta é a falha estrutural. O LFSR é um sistema linear: os n primeiros bits de saída **são** o estado inicial. Conhecido o polinômio, o atacante reconstrói o registrador e prevê todo o keystream futuro, demonstrado no teste, onde um clone reproduz exatamente os bits seguintes. No caso geral, o algoritmo de Berlekamp-Massey recupera tanto o estado quanto o polinômio a partir de 2n bits de keystream conhecido.
2. **Reúso de keystream (two-time pad).** Se duas mensagens são cifradas com a mesma semente, o keystream se cancela no XOR dos criptogramas:

   ```
   c₁ ⊕ c₂ = (p₁ ⊕ k) ⊕ (p₂ ⊕ k) = p₁ ⊕ p₂
   ```

   O atacante obtém a relação entre os textos claros sem conhecer a chave; conhecendo um deles, recupera o outro por inteiro. O teste demonstra isso recuperando uma ordem de transferência bancária completa.
3. **Estado nulo absorvente.** Semente zero trava o registrador em zeros permanentes, o XOR passa a devolver o texto claro intacto. A implementação rejeita essa semente na construção.
4. **Ausência de integridade.** Alterar um bit do criptograma altera exatamente o bit correspondente do texto claro, sem detecção. Um atacante que conheça o formato da mensagem pode modificá-la de forma dirigida.

### Decisões de implementação

- As funções `cifrar()` e `decifrar()` instanciam um LFSR **novo** a cada chamada. Reaproveitar o registrador entre chamadas faria a decifragem consumir um trecho diferente do keystream e devolver lixo, é um erro fácil de cometer com geradores com estado.
- A classe `LFSR` expõe `reiniciar()` e `periodo()` para inspeção didática.
- Validações rejeitam semente zero e expoentes fora do registrador na construção, não no uso.

---

## 4. Conclusão para o SecureDocs

Nenhuma das três cifras é adequada para proteger os documentos do SecureDocs:

- **Afim** cai por força bruta em milissegundos.
- **Vigenère** cai por análise estatística, mesmo com espaço de chaves grande.
- **LFSR puro** cai pela linearidade, com poucos bits de keystream conhecido.

O valor delas no projeto é conceitual e aponta três requisitos que as missões seguintes precisam atender:

1. **O espaço de chaves precisa ser grande o bastante** para inviabilizar busca exaustiva (lição da cifra afim).
2. **O criptograma não pode preservar estatísticas do texto claro**, difusão e confusão, no vocabulário de Shannon (lição de Vigenère).
3. **O gerador de keystream não pode ser linear**, e a chave nunca pode ser reutilizada entre mensagens (lição do LFSR).

Cifras de fluxo modernas, como ChaCha20, mantêm a estrutura de XOR com keystream, que é eficiente e simples, mas substituem o gerador linear por funções não lineares e adicionam um *nonce* por mensagem, eliminando exatamente as três falhas acima.

---

## Como executar os testes

Os módulos usam imports planos, então os testes rodam de dentro de `src/`:

```bash
cd src
python _t_cifras_classicas.py
python _t_cifra_fluxo.py
```