"""Implementacao educacional da cifra de Hill para matrizes quadradas."""

import math
import unicodedata

MODULO = 26


def _validar_matriz(matriz: list[list[int]]) -> None:
    if not matriz or any(len(linha) != len(matriz) for linha in matriz):
        raise ValueError("A chave deve ser uma matriz quadrada nao vazia.")


def _determinante(matriz: list[list[int]]) -> int:
    tamanho = len(matriz)
    if tamanho == 1:
        return matriz[0][0]
    if tamanho == 2:
        return matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]
    return sum(
        ((-1) ** coluna)
        * matriz[0][coluna]
        * _determinante(
            [linha[:coluna] + linha[coluna + 1 :] for linha in matriz[1:]]
        )
        for coluna in range(tamanho)
    )


def matriz_invertivel(chave: list[list[int]]) -> bool:
    """Informa se a matriz possui inversa no alfabeto de 26 letras."""
    _validar_matriz(chave)
    return math.gcd(_determinante(chave), MODULO) == 1


def _inverso_modular(numero: int) -> int:
    try:
        return pow(numero % MODULO, -1, MODULO)
    except ValueError as erro:
        raise ValueError(
            "A matriz-chave nao e invertivel no modulo 26; escolha outra chave."
        ) from erro


def _matriz_inversa(chave: list[list[int]]) -> list[list[int]]:
    _validar_matriz(chave)
    tamanho = len(chave)
    inverso_det = _inverso_modular(_determinante(chave))
    if tamanho == 1:
        return [[inverso_det]]

    cofatores = []
    for linha in range(tamanho):
        nova_linha = []
        for coluna in range(tamanho):
            menor = [
                l[:coluna] + l[coluna + 1 :]
                for indice, l in enumerate(chave)
                if indice != linha
            ]
            nova_linha.append(((-1) ** (linha + coluna)) * _determinante(menor))
        cofatores.append(nova_linha)

    adjunta = [list(linha) for linha in zip(*cofatores)]
    return [
        [(valor * inverso_det) % MODULO for valor in linha] for linha in adjunta
    ]


def _normalizar(texto: str) -> str:
    sem_acentos = unicodedata.normalize("NFD", texto)
    return "".join(
        caractere
        for caractere in sem_acentos.upper()
        if "A" <= caractere <= "Z"
    )


def _transformar(texto: str, matriz: list[list[int]]) -> str:
    tamanho = len(matriz)
    resultado = []
    for inicio in range(0, len(texto), tamanho):
        bloco = [ord(letra) - ord("A") for letra in texto[inicio : inicio + tamanho]]
        for linha in matriz:
            valor = sum(linha[i] * bloco[i] for i in range(tamanho)) % MODULO
            resultado.append(chr(valor + ord("A")))
    return "".join(resultado)


def cifrar_hill(texto: str, chave: list[list[int]], preenchimento: str = "X") -> str:
    """Cifra letras A-Z em blocos do tamanho da matriz-chave."""
    _validar_matriz(chave)
    if not matriz_invertivel(chave):
        raise ValueError("A matriz-chave nao e invertivel no modulo 26.")

    limpo = _normalizar(texto)
    letra_extra = _normalizar(preenchimento)
    if len(letra_extra) != 1:
        raise ValueError("O preenchimento deve ser uma unica letra de A a Z.")
    restante = len(limpo) % len(chave)
    if restante:
        limpo += letra_extra * (len(chave) - restante)
    return _transformar(limpo, chave)


def decifrar_hill(texto_cifrado: str, chave: list[list[int]]) -> str:
    """Decifra o texto com a inversa modular da matriz-chave."""
    _validar_matriz(chave)
    limpo = _normalizar(texto_cifrado)
    if len(limpo) % len(chave):
        raise ValueError("O texto cifrado deve conter blocos completos.")
    return _transformar(limpo, _matriz_inversa(chave))
