ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def cifrar(texto: str, chave: str) -> str:
    """
    cifra um texto utilizando uma cifra de substituição.

    cada letra do alfabeto é substituída pela letra
    correspondente na chave.
    """

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

    for caractere in texto:
        if caractere.upper() in ALFABETO:
            indice = ALFABETO.index(caractere.upper())
            substituto = chave[indice]

            if caractere.islower():
                resultado += substituto.lower()
            else:
                resultado += substituto
        else:
            resultado += caractere
    return resultado

def decifrar(texto: str, chave: str) -> str:
    """
    decifra um texto utilizando uma cifra de substituição

    a operação inversa da chave é utilizada para recuperar
    o texto original
    """

    if not isinstance(texto, str) or not isinstance(chave, str):
        raise ValueError("texto e chave devem ser strings")

    chave = chave.upper()

    if len(chave) != len(ALFABETO):
        raise ValueError("a chave deve possuir 26 letras")

    if len(set(chave)) != len(ALFABETO):
        raise ValueError("a chave deve possuir letras sem repetição")

    if not chave.isalpha():
        raise ValueError("a chave deve conter somente letras")

    resultado = ""

    for caractere in texto:
        if caractere.upper() in chave:
            indice = chave.index(caractere.upper())
            original = ALFABETO[indice]

            if caractere.islower():
                resultado += original.lower()
            else:
                resultado += original
        else:
            resultado += caractere

    return resultado