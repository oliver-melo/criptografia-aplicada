
# Implementação do algoritmo RC5
# RC5-32/12/16: palavras de 32 bits, 12 rodadas e chave de 16 bytes

MASCARA = 0xFFFFFFFF
P = 0xB7E15163
Q = 0x9E3779B9

RODADAS = 12


def rotacionar_esquerda(valor, quantidade):
    quantidade = quantidade % 32
    return ((valor << quantidade) | (valor >> (32 - quantidade))) & MASCARA


def rotacionar_direita(valor, quantidade):
    quantidade = quantidade % 32
    return ((valor >> quantidade) | (valor << (32 - quantidade))) & MASCARA


def expandir_chave(chave):
    if len(chave) == 0:
        raise ValueError("A chave não pode ser vazia.")

    tamanho_palavra = 4
    quantidade_palavras = max(1, (len(chave) + 3) // 4)

    L = [0] * quantidade_palavras

    for i in range(len(chave) - 1, -1, -1):
        L[i // 4] = ((L[i // 4] << 8) + chave[i]) & MASCARA

    quantidade_subchaves = 2 * (RODADAS + 1)

    S = [0] * quantidade_subchaves
    S[0] = P

    for i in range(1, quantidade_subchaves):
        S[i] = (S[i - 1] + Q) & MASCARA

    A = 0
    B = 0
    i = 0
    j = 0

    for _ in range(3 * max(quantidade_subchaves, quantidade_palavras)):
        A = S[i] = rotacionar_esquerda(
            (S[i] + A + B) & MASCARA, 3
        )

        B = L[j] = rotacionar_esquerda(
            (L[j] + A + B) & MASCARA, A + B
        )

        i = (i + 1) % quantidade_subchaves
        j = (j + 1) % quantidade_palavras

    return S


def cifrar(mensagem, subchaves):
    if len(mensagem) != 8:
        raise ValueError("A mensagem deve ter exatamente 8 bytes.")

    A = int.from_bytes(mensagem[:4], "little")
    B = int.from_bytes(mensagem[4:], "little")

    A = (A + subchaves[0]) & MASCARA
    B = (B + subchaves[1]) & MASCARA

    for i in range(1, RODADAS + 1):
        A = (rotacionar_esquerda(A ^ B, B) + subchaves[2 * i]) & MASCARA
        B = (rotacionar_esquerda(B ^ A, A) + subchaves[2 * i + 1]) & MASCARA

    return A.to_bytes(4, "little") + B.to_bytes(4, "little")


def decifrar(mensagem, subchaves):
    if len(mensagem) != 8:
        raise ValueError("A mensagem deve ter exatamente 8 bytes.")

    A = int.from_bytes(mensagem[:4], "little")
    B = int.from_bytes(mensagem[4:], "little")

    for i in range(RODADAS, 0, -1):
        B = rotacionar_direita(
            (B - subchaves[2 * i + 1]) & MASCARA, A
        ) ^ A

        A = rotacionar_direita(
            (A - subchaves[2 * i]) & MASCARA, B
        ) ^ B

    B = (B - subchaves[1]) & MASCARA
    A = (A - subchaves[0]) & MASCARA

    return A.to_bytes(4, "little") + B.to_bytes(4, "little")


# Teste da implementação
if __name__ == "__main__":
    chave = b"0123456789abcdef"
    mensagem_original = b"12345678"

    subchaves = expandir_chave(chave)

    mensagem_cifrada = cifrar(mensagem_original, subchaves)
    mensagem_decifrada = decifrar(mensagem_cifrada, subchaves)

    print("Mensagem original:", mensagem_original)
    print("Mensagem cifrada:", mensagem_cifrada.hex())
    print("Mensagem decifrada:", mensagem_decifrada)

    if mensagem_decifrada == mensagem_original:
        print("Teste concluído com sucesso!")
    else:
        print("Erro na implementação.")
