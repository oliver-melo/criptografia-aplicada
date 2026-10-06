class LFSR:
    
    def __init__(self, semente: int, polinomio: list[int], tamanho: int):
        if not isinstance(semente, int) or not isinstance(tamanho, int):
            raise ValueError("Semente e tamanho devem ser números inteiros.")
        if tamanho < 2:
            raise ValueError("O registrador deve ter ao menos 2 bits.")
        if semente == 0:
            raise ValueError(
                "A semente não pode ser zero: o estado nulo é absorvente e o "
                "registrador produziria apenas zeros para sempre."
            )
        if not polinomio or any(c < 1 or c > tamanho for c in polinomio):
            raise ValueError(
                f"Os expoentes do polinômio devem estar entre 1 e {tamanho}."
            )

        self.tamanho = tamanho
        self.polinomio = list(polinomio)
        self.indices = [tamanho - c for c in polinomio]  # expoente -> bit do estado
        self.semente = semente % (1 << tamanho)
        self.estado = self.semente

        if self.estado == 0:
            raise ValueError("A semente não pode ser congruente a zero no tamanho dado.")

    def __repr__(self):
        return f"LFSR(semente={self.semente}, polinomio={self.polinomio}, tamanho={self.tamanho})"

    def __str__(self):
        return f"LFSR de {self.tamanho} bits, estado atual {self.estado:0{self.tamanho}b}"

    def reiniciar(self) -> None:
        """Volta o registrador ao estado inicial (mesma semente)."""
        self.estado = self.semente

    def proximo_bit(self) -> int:
        """Avança o registrador em um passo e devolve o bit de saída."""

        bit_saida = self.estado & 1

        realimentacao = 0
        for indice in self.indices:
            realimentacao ^= (self.estado >> indice) & 1

        self.estado = (self.estado >> 1) | (realimentacao << (self.tamanho - 1))
        return bit_saida

    def keystream_bits(self, quantidade: int) -> list[int]:
        """Gera uma lista com os próximos `quantidade` bits do keystream."""
        return [self.proximo_bit() for _ in range(quantidade)]

    def keystream_bytes(self, quantidade: int) -> bytes:
        """Gera `quantidade` bytes do keystream (8 bits por byte)."""

        saida = bytearray()
        for _ in range(quantidade):
            byte = 0
            for _ in range(8):
                byte = (byte << 1) | self.proximo_bit()
            saida.append(byte)
        return bytes(saida)

    def periodo(self, limite: int = 1 << 20) -> int:

        copia = LFSR(self.semente, self.polinomio, self.tamanho)
        passos = 0

        while passos < limite:
            copia.proximo_bit()
            passos += 1
            if copia.estado == copia.semente:
                return passos

        raise ValueError(f"Período maior que o limite de {limite} passos.")


def cifrar(dados: bytes, semente: int, polinomio: list[int], tamanho: int) -> bytes:

    if not isinstance(dados, (bytes, bytearray)):
        raise ValueError("Os dados devem ser bytes.")

    gerador = LFSR(semente, polinomio, tamanho)
    keystream = gerador.keystream_bytes(len(dados))

    return bytes(d ^ k for d, k in zip(dados, keystream))


def decifrar(dados: bytes, semente: int, polinomio: list[int], tamanho: int) -> bytes:
    """Idêntica a cifrar(): no XOR, a operação é sua própria inversa."""
    return cifrar(dados, semente, polinomio, tamanho)


def cifrar_texto(texto: str, semente: int, polinomio: list[int], tamanho: int) -> bytes:
    """Cifra uma string, convertida para bytes em UTF-8."""
    return cifrar(texto.encode("utf-8"), semente, polinomio, tamanho)


def decifrar_texto(dados: bytes, semente: int, polinomio: list[int], tamanho: int) -> str:
    """Decifra bytes e reconstrói a string original."""
    return decifrar(dados, semente, polinomio, tamanho).decode("utf-8")


def ataque_reuso_de_chave(cifrado_a: bytes, cifrado_b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(cifrado_a, cifrado_b))