"""Testes e demonstração da classe DES de cifras_modernas.py para a Missão 3 do SecureDocs."""

from pathlib import Path
import tempfile

from cifras_modernas import DES


def teste_vetor_oficial_des() -> None:
    """Confere a implementação com um vetor de referência amplamente usado."""
    chave = bytes.fromhex("133457799BBCDFF1")
    mensagem = bytes.fromhex("0123456789ABCDEF")
    esperado = bytes.fromhex("85E813540F0AB405")

    cifrado = DES.encrypt_block(mensagem, chave)
    assert cifrado == esperado, (
        f"Falha no vetor DES: esperado {esperado.hex().upper()}, "
        f"obtido {cifrado.hex().upper()}"
    )
    assert DES.decrypt_block(cifrado, chave) == mensagem
    print("[OK] Vetor de referência DES validado.")
    print(f"     Texto claro : {mensagem.hex().upper()}")
    print(f"     Chave       : {chave.hex().upper()}")
    print(f"     Texto cifrado: {cifrado.hex().upper()}")


def exemplo_missao() -> None:
    """Demonstra o exemplo textual FLAMENGO / SEGREDOS."""
    mensagem = "FLAMENGO"
    chave = "SEGREDOS"  # 8 caracteres ASCII = 8 bytes

    cifrado = DES.encrypt_block(mensagem, chave)
    recuperado = DES.decrypt_block(cifrado, chave)

    print("\nEXEMPLO DIDÁTICO: DES")
    print(f"Mensagem original : {mensagem}")
    print(f"Chave             : {chave}")
    print(f"Mensagem cifrada : {cifrado.hex().upper()} (hexadecimal)")
    print(f"Mensagem decifrada: {recuperado.decode('utf-8')}")

    assert recuperado == mensagem.encode("utf-8")
    print("[OK] A mensagem original foi recuperada.")


def teste_arquivo() -> None:
    """Cifra e decifra um arquivo para demonstrar o fluxo da missão."""
    chave = "SEGREDOS"
    conteudo_original = (
        "TechSecure - SecureDocs\n"
        "Documento de teste da Missão 3.\n"
        "Este conteúdo será cifrado com DES em modo CBC.\n"
        "Após a decifragem, os bytes devem ser idênticos aos originais.\n"
    ).encode("utf-8")

    with tempfile.TemporaryDirectory(prefix="teste_securedocs_des_") as pasta_temp:
        pasta = Path(pasta_temp)
        arquivo_original = pasta / "documento_original.txt"
        arquivo_cifrado = pasta / "documento_cifrado.des"
        arquivo_recuperado = pasta / "documento_recuperado.txt"

        arquivo_original.write_bytes(conteudo_original)
        DES.encrypt_file(arquivo_original, arquivo_cifrado, chave)
        DES.decrypt_file(arquivo_cifrado, arquivo_recuperado, chave)

        bytes_originais = arquivo_original.read_bytes()
        bytes_recuperados = arquivo_recuperado.read_bytes()
        assert bytes_originais == bytes_recuperados

        print("\nTESTE DE ARQUIVO")
        print(f"Arquivo original  : {arquivo_original.name} ({len(bytes_originais)} bytes)")
        print(f"Arquivo cifrado   : {arquivo_cifrado.name} ({arquivo_cifrado.stat().st_size} bytes)")
        print(f"Arquivo recuperado: {arquivo_recuperado.name} ({len(bytes_recuperados)} bytes)")
        print(f"Conteúdo cifrado (início, hex): {arquivo_cifrado.read_bytes()[:48].hex().upper()}")
        print("Comparação original == recuperado: True")
        print("[OK] O arquivo foi recuperado sem diferenças.")


def teste_dados_em_memoria() -> None:
    """Confere também a API de cifragem de bytes."""
    original = b"Contrato confidencial do SecureDocs."
    chave = b"SEGREDOS"
    cifrado = DES.encrypt_bytes(original, chave)
    recuperado = DES.decrypt_bytes(cifrado, chave)
    assert recuperado == original
    print("[OK] Teste de encrypt_bytes/decrypt_bytes validado.")


if __name__ == "__main__":
    teste_vetor_oficial_des()
    exemplo_missao()
    teste_dados_em_memoria()
    teste_arquivo()
    print("\nTodos os testes foram concluídos com sucesso.")
