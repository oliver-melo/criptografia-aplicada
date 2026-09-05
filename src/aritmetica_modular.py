from MDC_ExponenciacaoModular import MDC
from euclides_estendido import euclides_estendido

class NumeroModular:
    """Implementa as operações fundamentais em espaços modulares."""
    
    def __init__(self, num: int, mod: int):
        if mod <= 0:
            raise ValueError("O módulo deve ser um número inteiro positivo.")
        self.num_mod = num % mod
        self.num = num
        self.mod = mod

    def __repr__(self):
        return f"NumeroModular({self.num}, {self.mod})"

    def __str__(self):
        return f"{self.num} (mod {self.mod})"

    def __eq__(self, other):
        if isinstance(other, NumeroModular):
            return self.num == other.num and self.mod == other.mod
        return False

    """Implementa operações modulares básicas: soma, subtração e multiplicação."""

    def __add__(self, other):
        if isinstance(other, NumeroModular):
            if self.mod != other.mod:
                raise ValueError("Os módulos devem ser iguais para a operação.")
            return NumeroModular((self.num_mod + other.num_mod) % self.mod, self.mod)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, NumeroModular):
            if self.mod != other.mod:
                raise ValueError("Os módulos devem ser iguais para a operação.")
            return NumeroModular((self.num_mod - other.num_mod) % self.mod, self.mod)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, NumeroModular):
            if self.mod != other.mod:
                raise ValueError("Os módulos devem ser iguais para a operação.")
            return NumeroModular((self.num_mod * other.num_mod) % self.mod, self.mod)
        return NotImplemented

    def inverso_multiplicativo(self) -> 'NumeroModular | None':
        mdc, x, y = euclides_estendido(self.num, self.mod)
        if mdc != 1:
            return None
        return NumeroModular(x % self.mod, self.mod)

    def __truediv__(self, other):
        if (self.mod != other.mod) :
            raise ValueError("Os módulos devem ser iguais para a operação.")
        inverso_other = other.inverso_multiplicativo()
        if inverso_other is None:
            raise ValueError(f"O inverso multiplicativo de {other.num_mod} não existe no módulo {other.mod}.")

        return self.__mul__(inverso_other)

    def __pow__(self, other: int) -> int:
        """Calcula (base ** expoente) mod modulo usando 'square and multiply'."""

        base = NumeroModular(self.num, self.mod)
        expoente = other

        if other < 0:
            inverso = base.inverso_multiplicativo()
            if inverso is None:
                raise ValueError(f"O inverso multiplicativo de {base.num_mod} não existe no módulo {base.mod}.")
            base = inverso
            expoente = -other
            
        resultado = NumeroModular(1, self.mod)

        while expoente > 0:
            if expoente % 2 == 1:
                resultado = (resultado * base)
            base = (base * base)
            expoente = expoente // 2

        return resultado


    def congruente(self, other: 'NumeroModular') -> bool:
        """
        Verifica se dois números modulares são congruentes.
        """
        if self.mod != other.mod:
            raise ValueError("Os módulos devem ser iguais para a operação.")

        return self.num_mod == other.num_mod

    