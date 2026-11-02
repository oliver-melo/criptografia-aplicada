import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

"""
AES (FIPS 197) no modo GCM (NIST SP 800-38D), via biblioteca `cryptography`.

Formato do criptograma: nonce (12 bytes) || texto cifrado || tag (16 bytes).
O nonce é gerado aleatoriamente (os.urandom) a cada cifragem e viaja junto
com o criptograma; a tag autentica texto cifrado, nonce e dados associados.
"""

TAMANHOS_CHAVE = (16, 24, 32)  # AES-128, AES-192, AES-256 (em bytes)
TAMANHO_NONCE = 12
TAMANHO_TAG = 16

"""funcoes auxiliares"""

def _validar_chave(chave: bytes) -> None:
    if not isinstance(chave, (bytes, bytearray)):
        raise ValueError("A chave deve ser bytes.")

    if len(chave) not in TAMANHOS_CHAVE:
        raise ValueError(
            f"Chave inválida: {len(chave)} bytes. Use 16, 24 ou 32 bytes "
            "(AES-128, AES-192 ou AES-256)."
        )

def _validar_dados(dados: bytes) -> None:
    if not isinstance(dados, (bytes, bytearray)):
        raise ValueError("Os dados devem ser bytes.")

def _validar_aad(aad: bytes | None) -> None:
    if aad is not None and not isinstance(aad, (bytes, bytearray)):
        raise ValueError("Os dados associados (aad) devem ser bytes ou None.")

"""geracao de chave"""

def gerar_chave(bits: int = 256) -> bytes:
    """Gera uma chave AES aleatória (128, 192 ou 256 bits) com os.urandom."""

    if bits not in (128, 192, 256):
        raise ValueError("O tamanho da chave deve ser 128, 192 ou 256 bits.")

    return os.urandom(bits // 8)

"""cifragem e decifragem"""

def cifrar(dados: bytes, chave: bytes, aad: bytes | None = None) -> bytes:
    """
    Cifra `dados` com AES-GCM e devolve nonce || texto cifrado || tag.

    `aad` são dados associados: autenticados, mas não cifrados. Quem decifrar
    precisa informar exatamente os mesmos.
    """

    _validar_chave(chave)
    _validar_dados(dados)
    _validar_aad(aad)

    nonce = os.urandom(TAMANHO_NONCE)
    cifrado_e_tag = AESGCM(bytes(chave)).encrypt(nonce, bytes(dados), aad)

    return nonce + cifrado_e_tag

def decifrar(criptograma: bytes, chave: bytes, aad: bytes | None = None) -> bytes:
    """
    Decifra e verifica um criptograma produzido por cifrar().

    Levanta ValueError se a chave for inválida, o criptograma estiver truncado
    ou a autenticação falhar (chave errada, dados, nonce, tag ou aad alterados).
    """

    _validar_chave(chave)
    _validar_dados(criptograma)
    _validar_aad(aad)

    if len(criptograma) < TAMANHO_NONCE + TAMANHO_TAG:
        raise ValueError(
            "Criptograma inválido: menor que nonce (12 bytes) + tag (16 bytes)."
        )

    nonce = bytes(criptograma[:TAMANHO_NONCE])
    cifrado_e_tag = bytes(criptograma[TAMANHO_NONCE:])

    try:
        return AESGCM(bytes(chave)).decrypt(nonce, cifrado_e_tag, aad)
    except InvalidTag as erro:
        raise ValueError(
            "Falha de autenticação: chave incorreta ou dados corrompidos/adulterados."
        ) from erro

def aes(dados: bytes, chave: bytes, modo: bool, aad: bytes | None = None) -> bytes:
    """
    Mesma convenção de chamada de metodos_cifragem:
    modo True cifra
    modo False decifra
    """

    if modo:
        return cifrar(dados, chave, aad)
    else:
        return decifrar(dados, chave, aad)

def cifrar_texto(texto: str, chave: bytes, aad: bytes | None = None) -> bytes:
    """Cifra uma string, convertida para bytes em UTF-8."""

    if not isinstance(texto, str):
        raise ValueError("O texto deve ser uma string.")

    return cifrar(texto.encode("utf-8"), chave, aad)

def decifrar_texto(criptograma: bytes, chave: bytes, aad: bytes | None = None) -> str:
    """Decifra um criptograma e reconstrói a string original."""
    return decifrar(criptograma, chave, aad).decode("utf-8")

"""arquivos"""

def cifrar_arquivo(entrada: str, saida: str, chave: bytes, aad: bytes | None = None) -> None:
    """
    Arquivo original -> AES-GCM -> arquivo cifrado.
    O arquivo inteiro é lido em memória (limite prático: o tamanho da RAM).
    """

    _validar_chave(chave)
    if os.path.abspath(entrada) == os.path.abspath(saida):
        raise ValueError("A saída deve ser um arquivo diferente da entrada.")

    with open(entrada, "rb") as f:
        dados = f.read()

    with open(saida, "wb") as f:
        f.write(cifrar(dados, chave, aad))

def decifrar_arquivo(entrada: str, saida: str, chave: bytes, aad: bytes | None = None) -> None:
    """
    Arquivo cifrado -> AES-GCM -> arquivo original.
    Nada é gravado em `saida` se a autenticação falhar.
    """

    _validar_chave(chave)
    if os.path.abspath(entrada) == os.path.abspath(saida):
        raise ValueError("A saída deve ser um arquivo diferente da entrada.")

    with open(entrada, "rb") as f:
        criptograma = f.read()

    dados = decifrar(criptograma, chave, aad)

    with open(saida, "wb") as f:
        f.write(dados)