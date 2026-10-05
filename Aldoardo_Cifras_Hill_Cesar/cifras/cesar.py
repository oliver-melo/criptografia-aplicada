"""Implementacao da cifra de Cesar."""


def _deslocar_caractere(caractere: str, deslocamento: int) -> str:
    if "A" <= caractere <= "Z":
        inicio = ord("A")
    elif "a" <= caractere <= "z":
        inicio = ord("a")
    else:
        return caractere

    return chr((ord(caractere) - inicio + deslocamento) % 26 + inicio)


def cifrar_cesar(texto: str, deslocamento: int) -> str:
    """Avanca cada letra pelo numero de posicoes informado."""
    return "".join(_deslocar_caractere(c, deslocamento) for c in texto)


def decifrar_cesar(texto_cifrado: str, deslocamento: int) -> str:
    """Desfaz a cifra, voltando o mesmo numero de posicoes."""
    return cifrar_cesar(texto_cifrado, -deslocamento)
