"""
Biblioteca Criptográfica - SecureDocs
Missão: MDC e Exponenciação Modular
"""


class MDC:
    """Implementa métodos relacionados ao Máximo Divisor Comum."""

    @staticmethod
    def mdc(a: int, b: int) -> int:
        """Calcula o MDC entre a e b usando o algoritmo de Euclides (iterativo)."""
        a, b = abs(a), abs(b)
        while b != 0:
            a, b = b, a % b
        return a

    @staticmethod
    def mdc_recursivo(a: int, b: int) -> int:
        """Mesma ideia de mdc(), mas implementada de forma recursiva."""
        a, b = abs(a), abs(b)
        if b == 0:
            return a
        return MDC.mdc_recursivo(b, a % b)

    @staticmethod
    def mdc_estendido(a: int, b: int):
        """Algoritmo de Euclides estendido: retorna (g, x, y) tal que a*x + b*y = g."""
        if b == 0:
            return a, 1, 0
        g, x1, y1 = MDC.mdc_estendido(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return g, x, y

    @staticmethod
    def inverso_modular(a: int, m: int) -> int:
        """Calcula o inverso multiplicativo de a módulo m (existe se mdc(a, m) == 1)."""
        g, x, _ = MDC.mdc_estendido(a, m)
        if g != 1:
            raise ValueError(f"Inverso modular não existe: mdc({a}, {m}) = {g}")
        return x % m


class ExponenciacaoModular:
    """Implementa métodos de exponenciação modular rápida."""

    @staticmethod
    def exp_modular(base: int, expoente: int, modulo: int) -> int:
        """Calcula (base ** expoente) mod modulo usando 'square and multiply'."""
        if modulo == 1:
            return 0

        if expoente < 0:
            base = MDC.inverso_modular(base, modulo)
            expoente = -expoente

        resultado = 1
        base = base % modulo

        while expoente > 0:
            if expoente & 1:
                resultado = (resultado * base) % modulo
            base = (base * base) % modulo
            expoente >>= 1

        return resultado

    @staticmethod
    def exp_modular_recursiva(base: int, expoente: int, modulo: int) -> int:
        """Mesma ideia de exp_modular(), mas implementada recursivamente."""
        if modulo == 1:
            return 0
        if expoente == 0:
            return 1 % modulo

        metade = ExponenciacaoModular.exp_modular_recursiva(base, expoente // 2, modulo)
        resultado = (metade * metade) % modulo

        if expoente % 2 == 1:
            resultado = (resultado * (base % modulo)) % modulo

        return resultado
