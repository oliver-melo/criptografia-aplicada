from __future__ import annotations

import os
from pathlib import Path
from typing import Union

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BytesLike = Union[bytes, bytearray, memoryview]
TextOrBytes = Union[str, BytesLike]


class RC5:
    """
    Implementação do algoritmo RC5 (RC5-32/12/16):
    palavras de 32 bits, 12 rodadas e chave padrão de 16 bytes.
    """

    MASCARA = 0xFFFFFFFF
    P = 0xB7E15163
    Q = 0x9E3779B9
    RODADAS = 12

    def __init__(self, chave: bytes | None = None):
        self.chave = chave
        self.subchaves = self.expandir_chave(chave) if chave is not None else None

    @staticmethod
    def rotacionar_esquerda(valor: int, quantidade: int) -> int:
        quantidade = quantidade % 32
        return ((valor << quantidade) | (valor >> (32 - quantidade))) & RC5.MASCARA

    @staticmethod
    def rotacionar_direita(valor: int, quantidade: int) -> int:
        quantidade = quantidade % 32
        return ((valor >> quantidade) | (valor << (32 - quantidade))) & RC5.MASCARA

    @classmethod
    def expandir_chave(cls, chave: bytes) -> list[int]:
        if len(chave) == 0:
            raise ValueError("A chave não pode ser vazia.")

        quantidade_palavras = max(1, (len(chave) + 3) // 4)
        L = [0] * quantidade_palavras

        for i in range(len(chave) - 1, -1, -1):
            L[i // 4] = ((L[i // 4] << 8) + chave[i]) & cls.MASCARA

        quantidade_subchaves = 2 * (cls.RODADAS + 1)

        S = [0] * quantidade_subchaves
        S[0] = cls.P

        for i in range(1, quantidade_subchaves):
            S[i] = (S[i - 1] + cls.Q) & cls.MASCARA

        A = 0
        B = 0
        i = 0
        j = 0

        for _ in range(3 * max(quantidade_subchaves, quantidade_palavras)):
            A = S[i] = cls.rotacionar_esquerda(
                (S[i] + A + B) & cls.MASCARA, 3
            )

            B = L[j] = cls.rotacionar_esquerda(
                (L[j] + A + B) & cls.MASCARA, A + B
            )

            i = (i + 1) % quantidade_subchaves
            j = (j + 1) % quantidade_palavras

        return S

    @classmethod
    def cifrar(cls, mensagem: bytes, subchaves: list[int]) -> bytes:
        if len(mensagem) != 8:
            raise ValueError("A mensagem deve ter exatamente 8 bytes.")

        A = int.from_bytes(mensagem[:4], "little")
        B = int.from_bytes(mensagem[4:], "little")

        A = (A + subchaves[0]) & cls.MASCARA
        B = (B + subchaves[1]) & cls.MASCARA

        for i in range(1, cls.RODADAS + 1):
            A = (cls.rotacionar_esquerda(A ^ B, B) + subchaves[2 * i]) & cls.MASCARA
            B = (cls.rotacionar_esquerda(B ^ A, A) + subchaves[2 * i + 1]) & cls.MASCARA

        return A.to_bytes(4, "little") + B.to_bytes(4, "little")

    @classmethod
    def decifrar(cls, mensagem: bytes, subchaves: list[int]) -> bytes:
        if len(mensagem) != 8:
            raise ValueError("A mensagem deve ter exatamente 8 bytes.")

        A = int.from_bytes(mensagem[:4], "little")
        B = int.from_bytes(mensagem[4:], "little")

        for i in range(cls.RODADAS, 0, -1):
            B = cls.rotacionar_direita(
                (B - subchaves[2 * i + 1]) & cls.MASCARA, A
            ) ^ A

            A = cls.rotacionar_direita(
                (A - subchaves[2 * i]) & cls.MASCARA, B
            ) ^ B

        B = (B - subchaves[1]) & cls.MASCARA
        A = (A - subchaves[0]) & cls.MASCARA

        return A.to_bytes(4, "little") + B.to_bytes(4, "little")


class DES:
    """
    Implementação do algoritmo DES (Data Encryption Standard)
    com suporte a cifragem de blocos isolados (ECB) e fluxos/arquivos em modo CBC com PKCS#7.
    """

    # Tabelas padrão do DES. As posições são numeradas a partir de 1, do bit mais
    # significativo para o menos significativo.
    _IP = [
        58, 50, 42, 34, 26, 18, 10, 2,
        60, 52, 44, 36, 28, 20, 12, 4,
        62, 54, 46, 38, 30, 22, 14, 6,
        64, 56, 48, 40, 32, 24, 16, 8,
        57, 49, 41, 33, 25, 17, 9, 1,
        59, 51, 43, 35, 27, 19, 11, 3,
        61, 53, 45, 37, 29, 21, 13, 5,
        63, 55, 47, 39, 31, 23, 15, 7,
    ]

    _FP = [
        40, 8, 48, 16, 56, 24, 64, 32,
        39, 7, 47, 15, 55, 23, 63, 31,
        38, 6, 46, 14, 54, 22, 62, 30,
        37, 5, 45, 13, 53, 21, 61, 29,
        36, 4, 44, 12, 52, 20, 60, 28,
        35, 3, 43, 11, 51, 19, 59, 27,
        34, 2, 42, 10, 50, 18, 58, 26,
        33, 1, 41, 9, 49, 17, 57, 25,
    ]

    _E = [
        32, 1, 2, 3, 4, 5,
        4, 5, 6, 7, 8, 9,
        8, 9, 10, 11, 12, 13,
        12, 13, 14, 15, 16, 17,
        16, 17, 18, 19, 20, 21,
        20, 21, 22, 23, 24, 25,
        24, 25, 26, 27, 28, 29,
        28, 29, 30, 31, 32, 1,
    ]

    _P = [
        16, 7, 20, 21, 29, 12, 28, 17,
        1, 15, 23, 26, 5, 18, 31, 10,
        2, 8, 24, 14, 32, 27, 3, 9,
        19, 13, 30, 6, 22, 11, 4, 25,
    ]

    _PC1 = [
        57, 49, 41, 33, 25, 17, 9,
        1, 58, 50, 42, 34, 26, 18,
        10, 2, 59, 51, 43, 35, 27,
        19, 11, 3, 60, 52, 44, 36,
        63, 55, 47, 39, 31, 23, 15,
        7, 62, 54, 46, 38, 30, 22,
        14, 6, 61, 53, 45, 37, 29,
        21, 13, 5, 28, 20, 12, 4,
    ]

    _PC2 = [
        14, 17, 11, 24, 1, 5,
        3, 28, 15, 6, 21, 10,
        23, 19, 12, 4, 26, 8,
        16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55,
        30, 40, 51, 45, 33, 48,
        44, 49, 39, 56, 34, 53,
        46, 42, 50, 36, 29, 32,
    ]

    _SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

    _SBOXES = [
        [
            [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
        ],
        [
            [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
            [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
            [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
            [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
        ],
        [
            [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
            [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
            [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
            [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
        ],
        [
            [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
            [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
            [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
            [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
        ],
        [
            [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
            [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
            [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
            [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
        ],
        [
            [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
            [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
            [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
            [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
        ],
        [
            [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
            [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
            [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
            [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
        ],
        [
            [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
            [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
            [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
            [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
        ],
    ]

    _MAGIC = b"SDES1"
    _BLOCK_SIZE = 8

    def __init__(self, key: TextOrBytes | None = None):
        self.key = self._validate_key(key) if key is not None else None

    @staticmethod
    def _as_bytes(value: TextOrBytes, name: str) -> bytes:
        if isinstance(value, str):
            return value.encode("utf-8")
        if isinstance(value, (bytes, bytearray, memoryview)):
            return bytes(value)
        raise TypeError(f"{name} deve ser str ou bytes.")

    @classmethod
    def _validate_key(cls, key: TextOrBytes) -> bytes:
        key_bytes = cls._as_bytes(key, "A chave")
        if len(key_bytes) != cls._BLOCK_SIZE:
            raise ValueError(
                "A chave DES deve possuir exatamente 8 bytes (64 bits; 56 bits efetivos)."
            )
        return key_bytes

    @staticmethod
    def _permute(value: int, table: list[int], input_bits: int) -> int:
        """Aplica uma permutação usando posições numeradas a partir do bit mais alto."""
        result = 0
        for position in table:
            result = (result << 1) | ((value >> (input_bits - position)) & 1)
        return result

    @classmethod
    def _generate_round_keys(cls, key: bytes) -> list[int]:
        key_64 = int.from_bytes(key, "big")
        key_56 = cls._permute(key_64, cls._PC1, 64)
        c = (key_56 >> 28) & 0x0FFFFFFF
        d = key_56 & 0x0FFFFFFF

        round_keys = []
        for shift in cls._SHIFTS:
            c = ((c << shift) & 0x0FFFFFFF) | (c >> (28 - shift))
            d = ((d << shift) & 0x0FFFFFFF) | (d >> (28 - shift))
            combined = (c << 28) | d
            round_keys.append(cls._permute(combined, cls._PC2, 56))
        return round_keys

    @classmethod
    def _feistel(cls, right: int, round_key: int) -> int:
        expanded = cls._permute(right, cls._E, 32)
        mixed = expanded ^ round_key

        substituted = 0
        for box_index in range(8):
            six_bits = (mixed >> (42 - 6 * box_index)) & 0x3F
            row = ((six_bits & 0b100000) >> 4) | (six_bits & 0b1)
            column = (six_bits >> 1) & 0x0F
            substituted = (substituted << 4) | cls._SBOXES[box_index][row][column]

        return cls._permute(substituted, cls._P, 32)

    @classmethod
    def _crypt_block(cls, block: bytes, round_keys: list[int]) -> bytes:
        if len(block) != cls._BLOCK_SIZE:
            raise ValueError("Um bloco DES deve possuir exatamente 8 bytes.")

        block_value = int.from_bytes(block, "big")
        permuted = cls._permute(block_value, cls._IP, 64)
        left = (permuted >> 32) & 0xFFFFFFFF
        right = permuted & 0xFFFFFFFF

        for round_key in round_keys:
            left, right = right, left ^ cls._feistel(right, round_key)

        # O DES aplica a permutação final sobre R16 || L16.
        pre_output = (right << 32) | left
        result = cls._permute(pre_output, cls._FP, 64)
        return result.to_bytes(cls._BLOCK_SIZE, "big")

    @classmethod
    def encrypt_block(cls, block: TextOrBytes, key: TextOrBytes) -> bytes:
        """Cifra exatamente um bloco de 8 bytes usando DES (modo ECB do bloco)."""
        block_bytes = cls._as_bytes(block, "O bloco")
        key_bytes = cls._validate_key(key)
        return cls._crypt_block(block_bytes, cls._generate_round_keys(key_bytes))

    @classmethod
    def decrypt_block(cls, block: TextOrBytes, key: TextOrBytes) -> bytes:
        """Decifra exatamente um bloco de 8 bytes usando DES."""
        block_bytes = cls._as_bytes(block, "O bloco")
        key_bytes = cls._validate_key(key)
        return cls._crypt_block(block_bytes, list(reversed(cls._generate_round_keys(key_bytes))))

    @classmethod
    def _pkcs7_pad(cls, data: bytes) -> bytes:
        padding_size = cls._BLOCK_SIZE - (len(data) % cls._BLOCK_SIZE)
        return data + bytes([padding_size]) * padding_size

    @classmethod
    def _pkcs7_unpad(cls, data: bytes) -> bytes:
        if not data or len(data) % cls._BLOCK_SIZE != 0:
            raise ValueError("Dados preenchidos inválidos.")
        padding_size = data[-1]
        if padding_size < 1 or padding_size > cls._BLOCK_SIZE:
            raise ValueError("Padding PKCS#7 inválido.")
        if data[-padding_size:] != bytes([padding_size]) * padding_size:
            raise ValueError("Padding PKCS#7 inválido.")
        return data[:-padding_size]

    @classmethod
    def encrypt_bytes(cls, data: TextOrBytes, key: TextOrBytes, iv: BytesLike | None = None) -> bytes:
        """Cifra dados em CBC e devolve assinatura + IV + blocos cifrados.

        O IV é gerado aleatoriamente quando não é informado. Para uso normal,
        deixe iv=None. O parâmetro existe para facilitar testes reproduzíveis.
        """
        plain = cls._as_bytes(data, "Os dados")
        key_bytes = cls._validate_key(key)

        if iv is None:
            iv_bytes = os.urandom(cls._BLOCK_SIZE)
        else:
            iv_bytes = bytes(iv)
            if len(iv_bytes) != cls._BLOCK_SIZE:
                raise ValueError("O IV do DES deve possuir exatamente 8 bytes.")

        round_keys = cls._generate_round_keys(key_bytes)
        padded = cls._pkcs7_pad(plain)
        previous = iv_bytes
        encrypted = bytearray()

        for offset in range(0, len(padded), cls._BLOCK_SIZE):
            block = padded[offset:offset + cls._BLOCK_SIZE]
            mixed = bytes(a ^ b for a, b in zip(block, previous))
            cipher_block = cls._crypt_block(mixed, round_keys)
            encrypted.extend(cipher_block)
            previous = cipher_block

        return cls._MAGIC + iv_bytes + bytes(encrypted)

    @classmethod
    def decrypt_bytes(cls, encrypted_data: BytesLike, key: TextOrBytes) -> bytes:
        """Decifra o formato produzido por encrypt_bytes."""
        encrypted = bytes(encrypted_data)
        key_bytes = cls._validate_key(key)

        minimum_size = len(cls._MAGIC) + cls._BLOCK_SIZE + cls._BLOCK_SIZE
        if len(encrypted) < minimum_size:
            raise ValueError("Arquivo cifrado muito pequeno ou formato inválido.")
        if not encrypted.startswith(cls._MAGIC):
            raise ValueError("Assinatura inválida: o conteúdo não parece ser um arquivo SDES1.")

        iv = encrypted[len(cls._MAGIC):len(cls._MAGIC) + cls._BLOCK_SIZE]
        ciphertext = encrypted[len(cls._MAGIC) + cls._BLOCK_SIZE:]
        if len(ciphertext) == 0 or len(ciphertext) % cls._BLOCK_SIZE != 0:
            raise ValueError("Tamanho do texto cifrado inválido.")

        round_keys = list(reversed(cls._generate_round_keys(key_bytes)))
        previous = iv
        plaintext = bytearray()

        for offset in range(0, len(ciphertext), cls._BLOCK_SIZE):
            cipher_block = ciphertext[offset:offset + cls._BLOCK_SIZE]
            decrypted_block = cls._crypt_block(cipher_block, round_keys)
            plaintext.extend(a ^ b for a, b in zip(decrypted_block, previous))
            previous = cipher_block

        return cls._pkcs7_unpad(bytes(plaintext))

    @classmethod
    def encrypt_file(cls, input_path: str | Path, output_path: str | Path, key: TextOrBytes) -> None:
        """Lê um arquivo, cifra seu conteúdo e grava o resultado em output_path."""
        source = Path(input_path)
        destination = Path(output_path)
        encrypted = cls.encrypt_bytes(source.read_bytes(), key)
        destination.write_bytes(encrypted)

    @classmethod
    def decrypt_file(cls, input_path: str | Path, output_path: str | Path, key: TextOrBytes) -> None:
        """Decifra um arquivo produzido por encrypt_file."""
        source = Path(input_path)
        destination = Path(output_path)
        decrypted = cls.decrypt_bytes(source.read_bytes(), key)
        destination.write_bytes(decrypted)


class AES:
    """
    AES (FIPS 197) no modo GCM (NIST SP 800-38D), via biblioteca `cryptography`.

    Formato do criptograma: nonce (12 bytes) || texto cifrado || tag (16 bytes).
    O nonce é gerado aleatoriamente (os.urandom) a cada cifragem e viaja junto
    com o criptograma; a tag autentica texto cifrado, nonce e dados associados.
    """

    TAMANHOS_CHAVE = (16, 24, 32)  # AES-128, AES-192, AES-256 (em bytes)
    TAMANHO_NONCE = 12
    TAMANHO_TAG = 16

    def __init__(self, chave: bytes | None = None):
        if chave is not None:
            self._validar_chave(chave)
        self.chave = chave

    @classmethod
    def _validar_chave(cls, chave: bytes) -> None:
        if not isinstance(chave, (bytes, bytearray)):
            raise ValueError("A chave deve ser bytes.")

        if len(chave) not in cls.TAMANHOS_CHAVE:
            raise ValueError(
                f"Chave inválida: {len(chave)} bytes. Use 16, 24 ou 32 bytes "
                "(AES-128, AES-192 ou AES-256)."
            )

    @staticmethod
    def _validar_dados(dados: bytes) -> None:
        if not isinstance(dados, (bytes, bytearray)):
            raise ValueError("Os dados devem ser bytes.")

    @staticmethod
    def _validar_aad(aad: bytes | None) -> None:
        if aad is not None and not isinstance(aad, (bytes, bytearray)):
            raise ValueError("Os dados associados (aad) devem ser bytes ou None.")

    @staticmethod
    def gerar_chave(bits: int = 256) -> bytes:
        """Gera uma chave AES aleatória (128, 192 ou 256 bits) com os.urandom."""
        if bits not in (128, 192, 256):
            raise ValueError("O tamanho da chave deve ser 128, 192 ou 256 bits.")
        return os.urandom(bits // 8)

    @classmethod
    def cifrar(cls, dados: bytes, chave: bytes, aad: bytes | None = None) -> bytes:
        """
        Cifra `dados` com AES-GCM e devolve nonce || texto cifrado || tag.

        `aad` são dados associados: autenticados, mas não cifrados. Quem decifrar
        precisa informar exatamente os mesmos.
        """
        cls._validar_chave(chave)
        cls._validar_dados(dados)
        cls._validar_aad(aad)

        nonce = os.urandom(cls.TAMANHO_NONCE)
        cifrado_e_tag = AESGCM(bytes(chave)).encrypt(nonce, bytes(dados), aad)

        return nonce + cifrado_e_tag

    @classmethod
    def decifrar(cls, criptograma: bytes, chave: bytes, aad: bytes | None = None) -> bytes:
        """
        Decifra e verifica um criptograma produzido por cifrar().

        Levanta ValueError se a chave for inválida, o criptograma estiver truncado
        ou a autenticação falhar (chave errada, dados, nonce, tag ou aad alterados).
        """
        cls._validar_chave(chave)
        cls._validar_dados(criptograma)
        cls._validar_aad(aad)

        if len(criptograma) < cls.TAMANHO_NONCE + cls.TAMANHO_TAG:
            raise ValueError(
                "Criptograma inválido: menor que nonce (12 bytes) + tag (16 bytes)."
            )

        nonce = bytes(criptograma[:cls.TAMANHO_NONCE])
        cifrado_e_tag = bytes(criptograma[cls.TAMANHO_NONCE:])

        try:
            return AESGCM(bytes(chave)).decrypt(nonce, cifrado_e_tag, aad)
        except InvalidTag as erro:
            raise ValueError(
                "Falha de autenticação: chave incorreta ou dados corrompidos/adulterados."
            ) from erro

    @classmethod
    def aes(cls, dados: bytes, chave: bytes, modo: bool, aad: bytes | None = None) -> bytes:
        """
        Mesma convenção de chamada de metodos_cifragem:
        modo True cifra
        modo False decifra
        """
        if modo:
            return cls.cifrar(dados, chave, aad)
        else:
            return cls.decifrar(dados, chave, aad)

    @classmethod
    def cifrar_texto(cls, texto: str, chave: bytes, aad: bytes | None = None) -> bytes:
        """Cifra uma string, convertida para bytes em UTF-8."""
        if not isinstance(texto, str):
            raise ValueError("O texto deve ser uma string.")
        return cls.cifrar(texto.encode("utf-8"), chave, aad)

    @classmethod
    def decifrar_texto(cls, criptograma: bytes, chave: bytes, aad: bytes | None = None) -> str:
        """Decifra um criptograma e reconstrói a string original."""
        return cls.decifrar(criptograma, chave, aad).decode("utf-8")

    @classmethod
    def cifrar_arquivo(cls, entrada: str, saida: str, chave: bytes, aad: bytes | None = None) -> None:
        """
        Arquivo original -> AES-GCM -> arquivo cifrado.
        O arquivo inteiro é lido em memória (limite prático: o tamanho da RAM).
        """
        cls._validar_chave(chave)
        if os.path.abspath(entrada) == os.path.abspath(saida):
            raise ValueError("A saída deve ser um arquivo diferente da entrada.")

        with open(entrada, "rb") as f:
            dados = f.read()

        with open(saida, "wb") as f:
            f.write(cls.cifrar(dados, chave, aad))

    @classmethod
    def decifrar_arquivo(cls, entrada: str, saida: str, chave: bytes, aad: bytes | None = None) -> None:
        """
        Arquivo cifrado -> AES-GCM -> arquivo original.
        Nada é gravado em `saida` se a autenticação falhar.
        """
        cls._validar_chave(chave)
        if os.path.abspath(entrada) == os.path.abspath(saida):
            raise ValueError("A saída deve ser um arquivo diferente da entrada.")

        with open(entrada, "rb") as f:
            criptograma = f.read()

        dados = cls.decifrar(criptograma, chave, aad)

        with open(saida, "wb") as f:
            f.write(dados)


if __name__ == "__main__":
    # Teste rápido de validação das três classes
    # 1. RC5
    chave_rc5 = b"0123456789abcdef"
    msg_rc5 = b"12345678"
    subchaves = RC5.expandir_chave(chave_rc5)
    cif_rc5 = RC5.cifrar(msg_rc5, subchaves)
    assert RC5.decifrar(cif_rc5, subchaves) == msg_rc5

    # 2. DES
    chave_des = b"8bytekey"
    msg_des = "Mensagem de teste para o DES!"
    cif_des = DES.encrypt_bytes(msg_des, chave_des)
    assert DES.decrypt_bytes(cif_des, chave_des).decode("utf-8") == msg_des

    # 3. AES
    chave_aes = AES.gerar_chave(256)
    msg_aes = "Mensagem secreta em AES-GCM!"
    cif_aes = AES.cifrar_texto(msg_aes, chave_aes)
    assert AES.decifrar_texto(cif_aes, chave_aes) == msg_aes

    print("Todos os testes (RC5, DES e AES) foram executados com sucesso!")
