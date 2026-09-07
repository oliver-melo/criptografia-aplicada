import math


def mdc(a: int, b: int) -> int:
    """
    Calcula MDC utilizando o algoritmo de Euclides.
    """

    if not isinstance(a, int) or not isinstance(b, int):
        raise ValueError("MDC só é definido para números inteiros.")

    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a

def is_prime(n: int) -> bool:

    """
    Verificação determinística (Divisão por tentativa).
    Recomendado apenas para fins didáticos e números pequenos.
    """

    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    
    """
    Otimização:
    verifica apenas números da forma 6k ± 1
    até a raiz quadrada de n.
    Reduz função f(n) = n
    para f(n) = (√n)*2/6 = (√n)/3;
    Reduz complexidade de O(n)
    para O(√n).
    """
    i = 6
    while math.isqrt(n) >= i:
        if n % (i - 1) == 0 or n % (i + 1) == 0:
            return False
        i += 6
    return True

def is_coprime(a: int, b: int) -> bool:
    """
    Verifica se dois números são coprimos (ou seja, seu MDC é 1).
    """
    return mdc(a, b) == 1

def euclides_estendido(a: int, b: int):
    """
    calcula o MDC de a e b e encontra os coeficientes x e y que satisfazem
    a*x + b*y = MDC(a,b).
    """

    if not isinstance(a, int) or not isinstance(b, int):
        raise ValueError("MDC só é definido para números inteiros.")

    def _calc(a: int, b: int) -> tuple[int, int, int]:
        if b == 0:
            return a, 1, 0
        mdc, x1, y1 = _calc(b, a % b)

        x = y1
        y = x1 - (a // b) * y1

        return mdc, x, y

    mdc, x, y = _calc(abs(a), abs(b))

    if a < 0: x = -x
    if b < 0: y = -y

    return mdc, x, y