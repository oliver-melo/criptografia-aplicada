import unicodedata

from algoritmos_fundamentais import is_coprime, totiente_euler
from numero_modular import NumeroModular

ALFABETO_PADRAO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def normalizar(texto: str) -> str:
    """
    Remove acentuação e converte para maiúsculas.

    """

    if not isinstance(texto, str):
        raise ValueError("O texto deve ser uma string.")

    decomposto = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return sem_acento.upper()


# ---------------------------------------------------------------------------
# Cifra de função Afim
# ---------------------------------------------------------------------------

def validar_chave_afim(a: int, b: int, alfabeto: str = ALFABETO_PADRAO) -> None:

    if not isinstance(a, int) or not isinstance(b, int):
        raise ValueError("As chaves a e b devem ser números inteiros.")

    m = len(alfabeto)
    if not is_coprime(a, m):
        raise ValueError(
            f"A chave a={a} não é coprima com o tamanho do alfabeto ({m}). "
            "Sem isso a cifra não é reversível."
        )


def chaves_afim_validas(alfabeto: str = ALFABETO_PADRAO) -> int:

    m = len(alfabeto)
    return totiente_euler(m) * m


def cifrar_afim(texto: str, a: int, b: int, alfabeto: str = ALFABETO_PADRAO) -> str:
    """
    Cifra afim: E(x) = (a*x + b) mod m

    """

    validar_chave_afim(a, b, alfabeto)
    m = len(alfabeto)
    resultado = []

    for caractere in normalizar(texto):
        if caractere not in alfabeto:
            resultado.append(caractere)
            continue

        x = alfabeto.index(caractere)
        y = NumeroModular(a * x + b, m).num_mod
        resultado.append(alfabeto[y])

    return "".join(resultado)


def decifrar_afim(texto: str, a: int, b: int, alfabeto: str = ALFABETO_PADRAO) -> str:
    """
    Inversa da cifra afim: D(y) = a⁻¹ * (y - b) mod m

    """

    validar_chave_afim(a, b, alfabeto)
    m = len(alfabeto)

    inverso = NumeroModular(a, m).inverso_multiplicativo()
    if inverso is None:
        raise ValueError(f"O inverso multiplicativo de {a} não existe no módulo {m}.")
    a_inv = inverso.num_mod

    resultado = []
    for caractere in normalizar(texto):
        if caractere not in alfabeto:
            resultado.append(caractere)
            continue

        y = alfabeto.index(caractere)
        x = NumeroModular(a_inv * (y - b), m).num_mod
        resultado.append(alfabeto[x])

    return "".join(resultado)


def forca_bruta_afim(texto: str, alfabeto: str = ALFABETO_PADRAO) -> list[tuple[int, int, str]]:
    """
    Ataque por força bruta: devolve (a, b, texto_decifrado) para toda
    chave válida.

    """

    m = len(alfabeto)
    tentativas = []

    for a in range(1, m):
        if not is_coprime(a, m):
            continue
        for b in range(m):
            tentativas.append((a, b, decifrar_afim(texto, a, b, alfabeto)))

    return tentativas


# ---------------------------------------------------------------------------
# Cifra de Vigenère
# ---------------------------------------------------------------------------

def _preparar_chave_vigenere(chave: str, alfabeto: str) -> list[int]:
    """Converte a chave em uma lista de deslocamentos."""

    chave_normalizada = [c for c in normalizar(chave) if c in alfabeto]
    if not chave_normalizada:
        raise ValueError("A chave deve conter ao menos uma letra do alfabeto.")

    return [alfabeto.index(c) for c in chave_normalizada]


def _aplicar_vigenere(texto: str, chave: str, alfabeto: str, sinal: int) -> str:

    deslocamentos = _preparar_chave_vigenere(chave, alfabeto)
    m = len(alfabeto)
    resultado = []
    posicao = 0

    for caractere in normalizar(texto):
        if caractere not in alfabeto:
            resultado.append(caractere)
            continue

        x = alfabeto.index(caractere)
        k = deslocamentos[posicao % len(deslocamentos)]
        y = NumeroModular(x + sinal * k, m).num_mod

        resultado.append(alfabeto[y])
        posicao += 1

    return "".join(resultado)


def cifrar_vigenere(texto: str, chave: str, alfabeto: str = ALFABETO_PADRAO) -> str:
    """
    Cifra de Vigenère: E(x_i) = (x_i + k_(i mod t)) mod m

    """

    return _aplicar_vigenere(texto, chave, alfabeto, +1)


def decifrar_vigenere(texto: str, chave: str, alfabeto: str = ALFABETO_PADRAO) -> str:
    """
    Inversa de Vigenère: D(y_i) = (y_i - k_(i mod t)) mod m
    
    """

    return _aplicar_vigenere(texto, chave, alfabeto, -1)


def indice_de_coincidencia(texto: str, alfabeto: str = ALFABETO_PADRAO) -> float:

    letras = [c for c in normalizar(texto) if c in alfabeto]
    n = len(letras)
    if n < 2:
        return 0.0

    total = 0
    for letra in alfabeto:
        f = letras.count(letra)
        total += f * (f - 1)

    return total / (n * (n - 1))


def estimar_tamanho_chave(texto: str, limite: int = 12, alfabeto: str = ALFABETO_PADRAO) -> list[tuple[int, float]]:
   
    letras = "".join(c for c in normalizar(texto) if c in alfabeto)
    resultados = []

    for t in range(1, limite + 1):
        fatias = [letras[i::t] for i in range(t)]
        medias = [indice_de_coincidencia(f, alfabeto) for f in fatias if len(f) > 1]
        if medias:
            resultados.append((t, sum(medias) / len(medias)))

    return sorted(resultados, key=lambda par: par[1], reverse=True)