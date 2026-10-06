import math
import unicodedata

"""Implementacao da cifra de Cesar."""

def cesar(texto: str, chave: int, modo: bool) -> str:

    if not isinstance(texto, str):
        raise ValueError("o texto deve ser uma string")

    if not isinstance(chave, int):
        raise ValueError("a chave deve ser um número inteiro")

    def _deslocar_caractere(caractere: str, deslocamento: int) -> str:
        if "A" <= caractere <= "Z":
            inicio = ord("A")
        elif "a" <= caractere <= "z":
            inicio = ord("a")
        else:
            return caractere

        return chr((ord(caractere) - inicio + deslocamento) % 26 + inicio)

    """
    Se modo True, avanca cada letra pelo numero de posicoes informado.
    Se modo False, retrocede cada letra pelo numero de posicoes informado.
    """
    deslocamento = chave if modo else -chave

    return "".join(_deslocar_caractere(c, deslocamento) for c in texto)

def substituicao(texto: str, chave: str, modo: bool) -> str:
    """
    Método da substituição: 
    cada letra do alfabeto é substituída pela letra
    correspondente na chave.
    
    modo True cifra
    modo False decifra
    """

    ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if not isinstance(texto, str) or not isinstance(chave, str):
        raise ValueError("texto e chave devem ser strings")

    chave =  chave.upper()

    if len(chave) != len(ALFABETO):
        raise ValueError("a chave deve possuir 26 letras")

    if len(set(chave)) != len(ALFABETO):
        raise ValueError("a chave deve possuir letras sem repetição")

    if not chave.isalpha():
        raise ValueError("a chave deve conter somente letras")

    resultado = ""

    if modo: 
        for caractere in texto:
            if caractere.upper() in ALFABETO:
                indice = ALFABETO.index(caractere.upper())
                substituto = chave[indice]
                resultado += substituto.lower() if caractere.islower() else substituto

            else: 
                """não é letra"""
                resultado += caractere

    else:
        for caractere in texto:
            if caractere.upper() in chave:
                indice = chave.index(caractere.upper())
                original = ALFABETO[indice]
                resultado += original.lower() if caractere.islower() else original

            else:
                """não é letra"""
                resultado += caractere

    return resultado

def transposicao(texto: str, chave: int, modo: bool) -> str:

    """
    Metodo de transposicao: 
    cifra um texto utilizando transposição por colunas.
    o texto é organizado em linhas com a quantidade de
    colunas definida pela chave e depois lido por colunas.
    
    modo True cifra
    modo False decifra
    """
    if not isinstance(texto, str):
        raise ValueError("o texto deve ser uma string")

    if not isinstance(chave, int) or chave <= 0:
        raise ValueError("a chave deve ser um número inteiro positivo")

    texto = texto.replace(" ", "")

    resultado = ""

    if modo:
        for coluna in range(chave):
            for posicao in range(coluna, len(texto), chave):
                resultado += texto[posicao]

        return resultado

    else:
        tamanho = len(texto)
        linhas = (tamanho + chave - 1) // chave

        resultado = [""] * tamanho
        indice = 0

        for coluna in range(chave):
            for linha in range(linhas):
                posicao = linha * chave + coluna

                if posicao < tamanho:
                    resultado[posicao] = texto[indice]
                    indice += 1

        return "".join(resultado)

def hill(texto: str, chave: list[list[int]], modo: bool) -> str:

    MODULO = 26

    def _validar_matriz(matriz: list[list[int]]) -> None:
        if not matriz or any(len(linha) != len(matriz) for linha in matriz):
            raise ValueError("A chave deve ser uma matriz quadrada nao vazia.")

    def _det(matriz: list[list[int]]) -> int:
        tamanho = len(matriz)
        if tamanho == 1:
            return matriz[0][0]
        if tamanho == 2:
            return matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]

        return sum(

            ((-1) ** coluna)
            *
            matriz[0][coluna]
            *
            _det(
                [linha[:coluna] + linha[coluna + 1 :] for linha in matriz[1:]]
            )
            for coluna in range(tamanho)

        )

    def matriz_invertivel(chave: list[list[int]]) -> bool:
        """Informa se a matriz possui inversa no alfabeto de 26 letras."""
        _validar_matriz(chave)
        return math.gcd(_det(chave), MODULO) == 1

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
        inverso_det = _inverso_modular(_det(chave))
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
                nova_linha.append(((-1) ** (linha + coluna)) * _det(menor))
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

    if modo:
        return cifrar_hill(texto, chave)
    else:
        return decifrar_hill(texto, chave)