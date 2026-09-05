class MDC:
    @staticmethod
    def mdc(a: int, b: int) -> int:
        if (a.is_integer() == False) or (b.is_integer() == False):
            raise ValueError("MDC só é definido para números inteiros.")
        a, b = abs(a), abs(b)
        while b != 0:
            a, b = b, a % b
        return a

