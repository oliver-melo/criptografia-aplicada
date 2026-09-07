import math

from aritmetica_modular import NumeroModular

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

def teorema_chines_do_resto(equacoes: list[NumeroModular]) -> NumeroModular:
    """
    equacoes: Uma lista de objetos NumeroModular representando as congruências 
              do tipo x ≡ num (mod m),
              onde m é o módulo de cada equação. 
                  
    Returns:
        Um objeto NumeroModular representando a solução x (mod M), 
        onde M é o produto de todos os módulos (m) do sistema.
    """

    tamanho = len(equacoes)
    
    # 1. Verificar se todos os módulos são coprimos entre si a pares
    for i in range(tamanho):
        for j in range(i + 1, tamanho):
            if not is_coprime(equacoes[i].mod, equacoes[j].mod):
                raise ValueError(
                    f"Os módulos {equacoes[i].mod} e {equacoes[j].mod} não são coprimos. "
                    "O teorema exige que os módulos sejam coprimos."
                )
    
    # 2. Calcular o M (produto de todos os módulos)
    M = 1
    for eq in equacoes:
        M *= eq.mod
        
    # 3. Calcular a solução (somatório de a_i * M_i * y_i)
    x_total = 0
    for eq in equacoes:
        a_i = eq.num_mod
        m_i = eq.mod
        
        # M_i é o produto de todos os módulos, exceto o módulo atual (m_i)
        M_i = M // m_i
        
        # Transforma M_i em NumeroModular para encontrar seu inverso mod m_i
        num_M_i = NumeroModular(M_i, m_i)
        y_i_modular = num_M_i.inverso_multiplicativo()
        
        if y_i_modular is None:
            raise ValueError(f"Inverso multiplicativo não encontrado para {M_i} mod {m_i}.")
            
        y_i = y_i_modular.num_mod
        
        # Somar o termo ao x_total
        x_total += a_i * M_i * y_i
        
    # 4. Retornar a solução já encapsulada na classe, que aplicará o módulo M automaticamente
    return NumeroModular(x_total, M)