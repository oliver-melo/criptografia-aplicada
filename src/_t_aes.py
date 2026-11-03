import os
import sys
import tempfile

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cifras_modernas import AES, DES, RC5

"""Testes do AES-GCM (classe AES de cifras_modernas.py)"""

falhas = []


def verificar(descricao: str, condicao: bool) -> None:
    print(f"[{'OK' if condicao else 'FALHA'}] {descricao}")
    if not condicao:
        falhas.append(descricao)


def levanta_valueerror(funcao, *args, **kwargs) -> bool:
    try:
        funcao(*args, **kwargs)
    except ValueError as erro:
        print(f"      ValueError: {erro}")
        return True
    return False


def alterar(dados: bytes, posicao: int) -> bytes:
    """Inverte um bit do byte na posição dada."""
    copia = bytearray(dados)
    copia[posicao] ^= 0x01
    return bytes(copia)


MENSAGEM = "Contrato confidencial da TechSecure — não divulgar.".encode("utf-8")


def teste_vetores_oficiais() -> None:
    print("\nVETORES OFICIAIS (FIPS 197 Apêndice C — bloco AES, modo ECB)")
    claro = bytes.fromhex("00112233445566778899aabbccddeeff")
    for bits, esperado in [
        (128, "69c4e0d86a7b0430d8cdb78070b4c55a"),
        (192, "dda97ca4864cdfe06eaf70a0ec0d7191"),
        (256, "8ea2b7ca516745bfeafc49904b496089"),
    ]:
        chave = bytes(range(bits // 8))
        cifrador = Cipher(algorithms.AES(chave), modes.ECB()).encryptor()
        bloco = cifrador.update(claro) + cifrador.finalize()
        verificar(f"AES-{bits}: bloco cifrado == {esperado}", bloco.hex() == esperado)

    print("\nVETORES OFICIAIS (NIST GCM, casos de teste 2, 8 e 14 — chave e IV zerados)")
    for bits, ct, tag in [
        (128, "0388dace60b6a392f328c2b971b2fe78", "ab6e47d42cec13bdf53a67b21257bddf"),
        (192, "98e7247c07f0fe411c267e4384b0f600", "2ff58d80033927ab8ef4d4587514f0fb"),
        (256, "cea7403d4d606b6e074ec5d3baf39d18", "d0d1c8a799996bf0265b98b5d48ab919"),
    ]:
        saida = AESGCM(bytes(bits // 8)).encrypt(bytes(12), bytes(16), None)
        verificar(f"AES-{bits}-GCM: texto cifrado e tag conferem", saida.hex() == ct + tag)
        verificar(
            f"AES-{bits}-GCM: AES.decifrar valida o vetor oficial",
            AES.decifrar(bytes(12) + saida, bytes(bits // 8)) == bytes(16),
        )


def teste_ida_e_volta_e_interfaces() -> None:
    print("\nIDA E VOLTA COM CHAVES DE 128, 192 E 256 BITS")
    for bits in (128, 192, 256):
        chave = AES.gerar_chave(bits)
        criptograma = AES.cifrar(MENSAGEM, chave)
        verificar(f"AES-{bits}: tamanho da chave = {len(chave) * 8} bits", len(chave) * 8 == bits)
        verificar(f"AES-{bits}: decifrar(cifrar(x)) == x", AES.decifrar(criptograma, chave) == MENSAGEM)
        verificar(
            f"AES-{bits}: criptograma = nonce + dados + tag ({len(criptograma)} bytes)",
            len(criptograma) == AES.TAMANHO_NONCE + len(MENSAGEM) + AES.TAMANHO_TAG,
        )
        verificar(f"AES-{bits}: texto claro não aparece no criptograma", MENSAGEM not in criptograma)

    print("\nTEXTO, DADOS BINÁRIOS GRANDES E INTERFACE AES.aes(modo)")
    chave = AES.gerar_chave(256)
    texto = "Relatório financeiro — ação, coração, 日本語"
    verificar(
        "cifrar_texto/decifrar_texto preserva acentos e Unicode",
        AES.decifrar_texto(AES.cifrar_texto(texto, chave), chave) == texto,
    )
    binario = os.urandom(1_000_003)
    verificar(
        "1 MB binário (tamanho não múltiplo de 16) recuperado exatamente",
        AES.decifrar(AES.cifrar(binario, chave), chave) == binario,
    )
    verificar(
        "AES.aes(modo=True/False) equivale a cifrar/decifrar",
        AES.aes(AES.aes(MENSAGEM, chave, True), chave, False) == MENSAGEM,
    )
    verificar(
        "bytearray é aceito como dados e como chave",
        AES.decifrar(AES.cifrar(bytearray(MENSAGEM), bytearray(chave)), bytearray(chave)) == MENSAGEM,
    )


def teste_nonce_e_chaves_incorretas() -> None:
    print("\nNONCE")
    chave = AES.gerar_chave(256)
    nonces = {AES.cifrar(MENSAGEM, chave)[:AES.TAMANHO_NONCE] for _ in range(10_000)}
    verificar("10.000 cifragens do mesmo dado com a mesma chave -> 10.000 nonces distintos", len(nonces) == 10_000)
    c1, c2 = AES.cifrar(MENSAGEM, chave), AES.cifrar(MENSAGEM, chave)
    verificar("mesmo texto e mesma chave produzem criptogramas diferentes", c1 != c2)

    print("\nCHAVE INCORRETA")
    chave_a, chave_b = AES.gerar_chave(256), AES.gerar_chave(256)
    verificar(
        "chave errada (mesmo tamanho) é rejeitada",
        levanta_valueerror(AES.decifrar, AES.cifrar(MENSAGEM, chave_a), chave_b),
    )
    verificar(
        "chave com 1 bit diferente é rejeitada",
        levanta_valueerror(AES.decifrar, AES.cifrar(MENSAGEM, chave_a), alterar(chave_a, 0)),
    )
    verificar(
        "chave de outro tamanho (AES-128 vs AES-256) é rejeitada",
        levanta_valueerror(AES.decifrar, AES.cifrar(MENSAGEM, chave_a), chave_a[:16]),
    )


def teste_adulteracao_e_aad() -> None:
    print("\nADULTERAÇÃO DO CRIPTOGRAMA (nonce, dados e tag)")
    chave = AES.gerar_chave(192)
    criptograma = AES.cifrar(MENSAGEM, chave)
    verificar("nonce alterado é detectado", levanta_valueerror(AES.decifrar, alterar(criptograma, 0), chave))
    verificar(
        "texto cifrado alterado é detectado",
        levanta_valueerror(AES.decifrar, alterar(criptograma, AES.TAMANHO_NONCE + 5), chave),
    )
    verificar(
        "tag alterada é detectado",
        levanta_valueerror(AES.decifrar, alterar(criptograma, len(criptograma) - 1), chave),
    )
    verificar(
        "tag substituída por zeros é detectada",
        levanta_valueerror(AES.decifrar, criptograma[:-AES.TAMANHO_TAG] + bytes(AES.TAMANHO_TAG), chave),
    )
    verificar("criptograma truncado (1 byte a menos) é detectado", levanta_valueerror(AES.decifrar, criptograma[:-1], chave))
    verificar("criptograma com byte extra é detectado", levanta_valueerror(AES.decifrar, criptograma + b"\x00", chave))
    verificar("criptograma menor que nonce+tag é rejeitado", levanta_valueerror(AES.decifrar, b"\x00" * 27, chave))

    def rejeita_silenciosamente(dados: bytes) -> bool:
        try:
            AES.decifrar(dados, chave)
        except ValueError:
            return True
        return False

    verificar(
        f"alterar qualquer um dos {len(criptograma)} bytes (1 bit) é sempre detectado",
        all(rejeita_silenciosamente(alterar(criptograma, i)) for i in range(len(criptograma))),
    )

    print("\nDADOS ASSOCIADOS (aad)")
    chave = AES.gerar_chave(128)
    cripto_aad = AES.cifrar(MENSAGEM, chave, aad=b"remetente=ana;doc=42")
    verificar("aad correto decifra", AES.decifrar(cripto_aad, chave, aad=b"remetente=ana;doc=42") == MENSAGEM)
    verificar("aad diferente é rejeitado", levanta_valueerror(AES.decifrar, cripto_aad, chave, aad=b"remetente=eva;doc=42"))
    verificar("aad omitido é rejeitado", levanta_valueerror(AES.decifrar, cripto_aad, chave))


def teste_entradas_invalidas_e_arquivos() -> None:
    print("\nENTRADAS VAZIAS E INVÁLIDAS")
    chave = AES.gerar_chave(256)
    vazio = AES.cifrar(b"", chave)
    verificar(f"dados vazios: cifra ({len(vazio)} bytes) e recupera b''", AES.decifrar(vazio, chave) == b"")
    verificar(
        "dados vazios: tag ainda autentica (adulteração detectada)",
        levanta_valueerror(AES.decifrar, alterar(vazio, len(vazio) - 1), chave),
    )
    verificar("criptograma vazio é rejeitado", levanta_valueerror(AES.decifrar, b"", chave))
    verificar("chave vazia é rejeitada", levanta_valueerror(AES.cifrar, MENSAGEM, b""))
    verificar("chave de 15 bytes é rejeitada", levanta_valueerror(AES.cifrar, MENSAGEM, os.urandom(15)))
    verificar("chave de 20 bytes é rejeitada", levanta_valueerror(AES.cifrar, MENSAGEM, os.urandom(20)))
    verificar("chave de 33 bytes é rejeitada", levanta_valueerror(AES.cifrar, MENSAGEM, os.urandom(33)))
    verificar("chave como str é rejeitada", levanta_valueerror(AES.cifrar, MENSAGEM, "0123456789abcdef"))
    verificar("chave None é rejeitada", levanta_valueerror(AES.cifrar, MENSAGEM, None))
    verificar("dados como str são rejeitados", levanta_valueerror(AES.cifrar, "texto", chave))
    verificar("dados None são rejeitados", levanta_valueerror(AES.cifrar, None, chave))
    verificar("aad como str é rejeitado", levanta_valueerror(AES.cifrar, MENSAGEM, chave, aad="x"))
    verificar("cifrar_texto rejeita bytes", levanta_valueerror(AES.cifrar_texto, b"x", chave))
    verificar("gerar_chave(100) é rejeitado", levanta_valueerror(AES.gerar_chave, 100))

    print("\nARQUIVO ORIGINAL -> AES -> CIFRADO -> AES -> ORIGINAL")
    with tempfile.TemporaryDirectory() as pasta:
        original = os.path.join(pasta, "contrato.bin")
        cifrado = os.path.join(pasta, "contrato.bin.aes")
        restaurado = os.path.join(pasta, "contrato_restaurado.bin")
        conteudo = os.urandom(300_000) + MENSAGEM
        with open(original, "wb") as f:
            f.write(conteudo)

        chave = AES.gerar_chave(256)
        AES.cifrar_arquivo(original, cifrado, chave)
        AES.decifrar_arquivo(cifrado, restaurado, chave)
        with open(cifrado, "rb") as f:
            bruto = f.read()
        with open(restaurado, "rb") as f:
            volta = f.read()
        verificar("arquivo cifrado difere do original e não contém o texto claro", bruto != conteudo and MENSAGEM not in bruto)
        verificar("arquivo restaurado é idêntico ao original", volta == conteudo)

        with open(cifrado, "wb") as f:
            f.write(alterar(bruto, 1000))
        apagado = os.path.join(pasta, "nao_deve_existir.bin")
        verificar("arquivo cifrado adulterado é rejeitado", levanta_valueerror(AES.decifrar_arquivo, cifrado, apagado, chave))
        verificar("nada é gravado quando a autenticação falha", not os.path.exists(apagado))
        verificar("entrada == saída é rejeitado", levanta_valueerror(AES.cifrar_arquivo, original, original, chave))


def teste_compatibilidade_cifras_modernas() -> None:
    print("\nCOMPATIBILIDADE COM AS DEMAIS CLASSES DE cifras_modernas.py (RC5 e DES)")
    chave_aes = AES.gerar_chave(256)
    sub_rc5 = RC5.expandir_chave(b"0123456789abcdef")
    bloco_rc5 = RC5.cifrar(b"12345678", sub_rc5)
    verificar("classe RC5 continua funcionando no mesmo módulo", RC5.decifrar(bloco_rc5, sub_rc5) == b"12345678")

    pacote_des = DES.encrypt_bytes(MENSAGEM, b"SEGREDOS")
    verificar("classe DES continua funcionando no mesmo módulo", DES.decrypt_bytes(pacote_des, b"SEGREDOS") == MENSAGEM)
    verificar(
        "AES sobre o criptograma do DES (encadeamento) recupera o original",
        DES.decrypt_bytes(AES.decifrar(AES.cifrar(pacote_des, chave_aes), chave_aes), b"SEGREDOS") == MENSAGEM,
    )


if __name__ == "__main__":
    teste_vetores_oficiais()
    teste_ida_e_volta_e_interfaces()
    teste_nonce_e_chaves_incorretas()
    teste_adulteracao_e_aad()
    teste_entradas_invalidas_e_arquivos()
    teste_compatibilidade_cifras_modernas()

    print()
    if falhas:
        print(f"{len(falhas)} TESTE(S) FALHARAM:")
        for descricao in falhas:
            print(f"  - {descricao}")
        sys.exit(1)
    print("TODOS OS TESTES PASSARAM")
