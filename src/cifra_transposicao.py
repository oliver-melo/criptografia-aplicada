def cifrar(texto: str, chave: int) -> str:
    """
    cifra um texto utilizando transposição por colunas

    o texto é organizado em linhas com a quantidade de
    colunas definida pela chave e depois lido por colunas
    """
    if not isinstance(texto, str):
        raise ValueError("o texto deve ser uma string")

    if not isinstance(chave, int) or chave <= 0:
        raise ValueError("a chave deve ser um número inteiro positivo")

    texto = texto.replace(" ", "")

    resultado = ""

    for coluna in range(chave):
        for posicao in range(coluna, len(texto), chave):
            resultado += texto[posicao]

    return resultado


def decifrar(texto: str, chave: int) -> str:
    """
    decifra um texto utilizando transposição por colunas

    a operação inversa reorganiza o texto cifrado nas colunas
    para recuperar a mensagem original
    """
    if not isinstance(texto, str):
        raise ValueError("o texto deve ser uma string")

    if not isinstance(chave, int) or chave <= 0:
        raise ValueError("a chave deve ser um número inteiro positivo")

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