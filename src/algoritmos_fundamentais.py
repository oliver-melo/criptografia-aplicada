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

def fatoracao_prima(n: int) -> dict[int, int]:
    """
    Fatora n em seus primos, retornando um dicionário {primo: expoente}.

    """

    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError("A fatoração só é definida para números inteiros.")
    if n < 2:
        return {}

    fatores: dict[int, int] = {}
    resto = n

    divisor = 2
    while divisor * divisor <= resto:
        while resto % divisor == 0:
            fatores[divisor] = fatores.get(divisor, 0) + 1
            resto //= divisor
        divisor += 1 if divisor == 2 else 2  # 2, depois só ímpares

    if resto > 1:
        fatores[resto] = fatores.get(resto, 0) + 1

    return fatores


def totiente_euler(n: int) -> int:
    """
    Função φ (totiente) de Euler: quantidade de inteiros em [1, n]
    que são coprimos com n.

    Implementada pela fórmula do produto sobre os fatores primos
    distintos de n:

        φ(n) = n * Π (1 - 1/p),  para cada primo p que divide n


    """

    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError("A função φ de Euler só é definida para números inteiros.")
    if n < 1:
        raise ValueError("A função φ de Euler só é definida para inteiros positivos.")

    resultado = n
    for primo in fatoracao_prima(n):
        resultado -= resultado // primo

    return resultado  # φ(1) = 1, pois 1 não possui fatores primos


def totiente_euler_ingenuo(n: int) -> int:
    """
    Versão didática da função φ: conta diretamente quantos k em [1, n]
    satisfazem mdc(k, n) = 1.

    """

    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError("A função φ de Euler só é definida para números inteiros.")
    if n < 1:
        raise ValueError("A função φ de Euler só é definida para inteiros positivos.")

    return sum(1 for k in range(1, n + 1) if is_coprime(k, n))