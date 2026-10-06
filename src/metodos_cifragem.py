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
        raise ValueError("testo e chave devem ser strings")

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