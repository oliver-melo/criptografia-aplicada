"""Testes e demonstração da classe RC5 (RC5-32/12/16) de cifras_modernas.py."""

from cifras_modernas import RC5


def teste_vetores_oficiais_rc5() -> None:
    """
    Confere a implementação com os 5 vetores de referência de R. Rivest (1994) / RFC 2040
    para o RC5-32/12/16 (Apêndice A de 'The RC5 Encryption Algorithm').
    """
    vetores = [
        (
            "00000000000000000000000000000000",
            "0000000000000000",
            "21a5dbee154b8f6d",
        ),
        (
            "915f4619be41b2516355a50110a9ce91",
            "21a5dbee154b8f6d",
            "f7c013ac5b2b8952",
        ),
        (
            "783348e75aeb0f2fd7b169bb8dc16787",
            "f7c013ac5b2b8952",
            "2f42b3b70369fc92",
        ),
        (
            "dc49db1375a5584f6485b413b5f12baf",
            "2f42b3b70369fc92",
            "65c178b284d197cc",
        ),
        (
            "5269f149d41ba0152497574d7f153125",
            "65c178b284d197cc",
            "eb44e415da319824",
        ),
    ]

    print("VETORES DE REFERÊNCIA RC5-32/12/16 (Rivest, 1994 / RFC 2040)")
    for indice, (chave_hex, claro_hex, esperado_hex) in enumerate(vetores, start=1):
        chave = bytes.fromhex(chave_hex)
        mensagem = bytes.fromhex(claro_hex)
        esperado = bytes.fromhex(esperado_hex)

        subchaves = RC5.expandir_chave(chave)
        assert len(subchaves) == 2 * (RC5.RODADAS + 1)

        cifrado = RC5.cifrar(mensagem, subchaves)
        assert cifrado == esperado, (
            f"Falha no vetor RC5 #{indice}: esperado {esperado.hex().upper()}, "
            f"obtido {cifrado.hex().upper()}"
        )
        assert RC5.decifrar(cifrado, subchaves) == mensagem
        print(f"[OK] Vetor #{indice} validado -> Cifrado: {cifrado.hex().upper()}")


def exemplo_didatico_rc5() -> None:
    """Demonstra o exemplo original da implementação do RC5-32/12/16."""
    chave = b"0123456789abcdef"  # 16 bytes
    mensagem_original = b"12345678"  # 8 bytes (2 palavras de 32 bits)

    subchaves = RC5.expandir_chave(chave)
    mensagem_cifrada = RC5.cifrar(mensagem_original, subchaves)
    mensagem_decifrada = RC5.decifrar(mensagem_cifrada, subchaves)

    print("\nEXEMPLO DIDÁTICO: RC5-32/12/16")
    print(f"Mensagem original : {mensagem_original.decode('utf-8')}")
    print(f"Chave (16 bytes)  : {chave.decode('utf-8')}")
    print(f"Mensagem cifrada  : {mensagem_cifrada.hex().upper()} (hexadecimal)")
    print(f"Mensagem decifrada: {mensagem_decifrada.decode('utf-8')}")

    assert mensagem_decifrada == mensagem_original
    print("[OK] A mensagem original foi recuperada.")


def teste_rotacoes_e_validacoes() -> None:
    """Confere as rotações modulares de 32 bits e o tratamento de entradas inválidas."""
    valor = 0x12345678
    rot_esq = RC5.rotacionar_esquerda(valor, 8)
    rot_dir = RC5.rotacionar_direita(rot_esq, 8)
    assert rot_dir == valor
    print("\n[OK] Rotações circulares de 32 bits (esquerda/direita) validadas.")

    # Chave vazia deve levantar ValueError
    try:
        RC5.expandir_chave(b"")
        raise AssertionError("Deveria rejeitar chave vazia.")
    except ValueError as erro:
        print(f"[OK] Rejeição de chave vazia validada ({erro})")

    # Bloco com tamanho diferente de 8 bytes deve levantar ValueError
    subchaves = RC5.expandir_chave(b"0123456789abcdef")
    for invalido in (b"curto", b"bloco_com_mais_de_8_bytes"):
        try:
            RC5.cifrar(invalido, subchaves)
            raise AssertionError("Deveria rejeitar bloco com tamanho != 8 bytes.")
        except ValueError as erro:
            print(f"[OK] Rejeição de bloco inválido ({len(invalido)} bytes) validada ({erro})")


if __name__ == "__main__":
    teste_vetores_oficiais_rc5()
    exemplo_didatico_rc5()
    teste_rotacoes_e_validacoes()
    print("\nTodos os testes do RC5 foram concluídos com sucesso.")
