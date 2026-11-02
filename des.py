
from __future__ import annotations

import os
from pathlib import Path
from typing import Union

BytesLike = Union[bytes, bytearray, memoryview]
TextOrBytes = Union[str, BytesLike]

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


def _as_bytes(value: TextOrBytes, name: str) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value)
    raise TypeError(f"{name} deve ser str ou bytes.")


def _validate_key(key: TextOrBytes) -> bytes:
    key_bytes = _as_bytes(key, "A chave")
    if len(key_bytes) != _BLOCK_SIZE:
        raise ValueError(
            "A chave DES deve possuir exatamente 8 bytes (64 bits; 56 bits efetivos)."
        )
    return key_bytes


def _permute(value: int, table: list[int], input_bits: int) -> int:
    """Aplica uma permutação usando posições numeradas a partir do bit mais alto."""
    result = 0
    for position in table:
        result = (result << 1) | ((value >> (input_bits - position)) & 1)
    return result


def _generate_round_keys(key: bytes) -> list[int]:
    key_64 = int.from_bytes(key, "big")
    key_56 = _permute(key_64, _PC1, 64)
    c = (key_56 >> 28) & 0x0FFFFFFF
    d = key_56 & 0x0FFFFFFF

    round_keys = []
    for shift in _SHIFTS:
        c = ((c << shift) & 0x0FFFFFFF) | (c >> (28 - shift))
        d = ((d << shift) & 0x0FFFFFFF) | (d >> (28 - shift))
        combined = (c << 28) | d
        round_keys.append(_permute(combined, _PC2, 56))
    return round_keys


def _feistel(right: int, round_key: int) -> int:
    expanded = _permute(right, _E, 32)
    mixed = expanded ^ round_key

    substituted = 0
    for box_index in range(8):
        six_bits = (mixed >> (42 - 6 * box_index)) & 0x3F
        row = ((six_bits & 0b100000) >> 4) | (six_bits & 0b1)
        column = (six_bits >> 1) & 0x0F
        substituted = (substituted << 4) | _SBOXES[box_index][row][column]

    return _permute(substituted, _P, 32)


def _crypt_block(block: bytes, round_keys: list[int]) -> bytes:
    if len(block) != _BLOCK_SIZE:
        raise ValueError("Um bloco DES deve possuir exatamente 8 bytes.")

    block_value = int.from_bytes(block, "big")
    permuted = _permute(block_value, _IP, 64)
    left = (permuted >> 32) & 0xFFFFFFFF
    right = permuted & 0xFFFFFFFF

    for round_key in round_keys:
        left, right = right, left ^ _feistel(right, round_key)

    # O DES aplica a permutação final sobre R16 || L16.
    pre_output = (right << 32) | left
    result = _permute(pre_output, _FP, 64)
    return result.to_bytes(_BLOCK_SIZE, "big")


def encrypt_block(block: TextOrBytes, key: TextOrBytes) -> bytes:
    """Cifra exatamente um bloco de 8 bytes usando DES (modo ECB do bloco)."""
    block_bytes = _as_bytes(block, "O bloco")
    key_bytes = _validate_key(key)
    return _crypt_block(block_bytes, _generate_round_keys(key_bytes))


def decrypt_block(block: TextOrBytes, key: TextOrBytes) -> bytes:
    """Decifra exatamente um bloco de 8 bytes usando DES."""
    block_bytes = _as_bytes(block, "O bloco")
    key_bytes = _validate_key(key)
    return _crypt_block(block_bytes, list(reversed(_generate_round_keys(key_bytes))))


def _pkcs7_pad(data: bytes) -> bytes:
    padding_size = _BLOCK_SIZE - (len(data) % _BLOCK_SIZE)
    return data + bytes([padding_size]) * padding_size


def _pkcs7_unpad(data: bytes) -> bytes:
    if not data or len(data) % _BLOCK_SIZE != 0:
        raise ValueError("Dados preenchidos inválidos.")
    padding_size = data[-1]
    if padding_size < 1 or padding_size > _BLOCK_SIZE:
        raise ValueError("Padding PKCS#7 inválido.")
    if data[-padding_size:] != bytes([padding_size]) * padding_size:
        raise ValueError("Padding PKCS#7 inválido.")
    return data[:-padding_size]


def encrypt_bytes(data: TextOrBytes, key: TextOrBytes, iv: BytesLike | None = None) -> bytes:
    """Cifra dados em CBC e devolve assinatura + IV + blocos cifrados.

    O IV é gerado aleatoriamente quando não é informado. Para uso normal,
    deixe iv=None. O parâmetro existe para facilitar testes reproduzíveis.
    """
    plain = _as_bytes(data, "Os dados")
    key_bytes = _validate_key(key)

    if iv is None:
        iv_bytes = os.urandom(_BLOCK_SIZE)
    else:
        iv_bytes = bytes(iv)
        if len(iv_bytes) != _BLOCK_SIZE:
            raise ValueError("O IV do DES deve possuir exatamente 8 bytes.")

    round_keys = _generate_round_keys(key_bytes)
    padded = _pkcs7_pad(plain)
    previous = iv_bytes
    encrypted = bytearray()

    for offset in range(0, len(padded), _BLOCK_SIZE):
        block = padded[offset:offset + _BLOCK_SIZE]
        mixed = bytes(a ^ b for a, b in zip(block, previous))
        cipher_block = _crypt_block(mixed, round_keys)
        encrypted.extend(cipher_block)
        previous = cipher_block

    return _MAGIC + iv_bytes + bytes(encrypted)


def decrypt_bytes(encrypted_data: BytesLike, key: TextOrBytes) -> bytes:
    """Decifra o formato produzido por encrypt_bytes."""
    encrypted = bytes(encrypted_data)
    key_bytes = _validate_key(key)

    minimum_size = len(_MAGIC) + _BLOCK_SIZE + _BLOCK_SIZE
    if len(encrypted) < minimum_size:
        raise ValueError("Arquivo cifrado muito pequeno ou formato inválido.")
    if not encrypted.startswith(_MAGIC):
        raise ValueError("Assinatura inválida: o conteúdo não parece ser um arquivo SDES1.")

    iv = encrypted[len(_MAGIC):len(_MAGIC) + _BLOCK_SIZE]
    ciphertext = encrypted[len(_MAGIC) + _BLOCK_SIZE:]
    if len(ciphertext) == 0 or len(ciphertext) % _BLOCK_SIZE != 0:
        raise ValueError("Tamanho do texto cifrado inválido.")

    round_keys = list(reversed(_generate_round_keys(key_bytes)))
    previous = iv
    plaintext = bytearray()

    for offset in range(0, len(ciphertext), _BLOCK_SIZE):
        cipher_block = ciphertext[offset:offset + _BLOCK_SIZE]
        decrypted_block = _crypt_block(cipher_block, round_keys)
        plaintext.extend(a ^ b for a, b in zip(decrypted_block, previous))
        previous = cipher_block

    return _pkcs7_unpad(bytes(plaintext))


def encrypt_file(input_path: str | Path, output_path: str | Path, key: TextOrBytes) -> None:
    """Lê um arquivo, cifra seu conteúdo e grava o resultado em output_path."""
    source = Path(input_path)
    destination = Path(output_path)
    encrypted = encrypt_bytes(source.read_bytes(), key)
    destination.write_bytes(encrypted)


def decrypt_file(input_path: str | Path, output_path: str | Path, key: TextOrBytes) -> None:
    """Decifra um arquivo produzido por encrypt_file."""
    source = Path(input_path)
    destination = Path(output_path)
    decrypted = decrypt_bytes(source.read_bytes(), key)
    destination.write_bytes(decrypted)
