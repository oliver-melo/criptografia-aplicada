from cifra_fluxo import (
    LFSR,
    cifrar,
    decifrar,
    cifrar_texto,
    decifrar_texto,
    ataque_reuso_de_chave,
)

"""Testes da cifra de fluxo baseada em LFSR"""

POLINOMIO_4 = [4, 3]
POLINOMIO_16 = [16, 14, 13, 11]

print("\nGERAÇÃO DE KEYSTREAM — LFSR de 4 bits")
r = LFSR(semente=0b1001, polinomio=POLINOMIO_4, tamanho=4)
print(r)
print(f"Primeiros 15 bits: {''.join(str(b) for b in r.keystream_bits(15))}")

print("\nPERÍODO")
r4 = LFSR(0b1001, POLINOMIO_4, 4)
r16 = LFSR(0xACE1, POLINOMIO_16, 16)
print(f"LFSR  4 bits -> período {r4.periodo()}   (máximo teórico 2^4  - 1 = 15)")
print(f"LFSR 16 bits -> período {r16.periodo()}  (máximo teórico 2^16 - 1 = 65535)")

print("\nCIFRAGEM E DECIFRAGEM DE TEXTO")
mensagem = "Contrato confidencial da TechSecure — não divulgar."
semente = 0xACE1
cifrado = cifrar_texto(mensagem, semente, POLINOMIO_16, 16)
print(f"Claro:    {mensagem}")
print(f"Cifrado:  {cifrado.hex()}")
print(f"Decifrado:{decifrar_texto(cifrado, semente, POLINOMIO_16, 16)}")

print("\nSIMETRIA DO XOR — cifrar e decifrar são a mesma função")
dados = b"SecureDocs"
ida = cifrar(dados, semente, POLINOMIO_16, 16)
volta = cifrar(ida, semente, POLINOMIO_16, 16)  # a MESMA função, não decifrar()
print(f"cifrar(cifrar(x)) == x ? {volta == dados}")
print(f"decifrar == cifrar ?     {decifrar(ida, semente, POLINOMIO_16, 16) == dados}")

print("\nEFEITO AVALANCHE NA CHAVE — 1 bit de diferença na semente")
c1 = cifrar(b"SecureDocs", 0xACE1, POLINOMIO_16, 16)
c2 = cifrar(b"SecureDocs", 0xACE0, POLINOMIO_16, 16)  # último bit alterado
print(f"semente 0xACE1 -> {c1.hex()}")
print(f"semente 0xACE0 -> {c2.hex()}")
print(f"Bytes diferentes: {sum(1 for x, y in zip(c1, c2) if x != y)} de {len(c1)}")

print("\nSEMENTES INVÁLIDAS")
for sem, polin, tam, rotulo in [
    (0, POLINOMIO_4, 4, "semente zero"),
    (0b1001, [], 4, "sem polinômio"),
    (0b1001, [9], 4, "expoente fora do registrador"),
]:
    try:
        LFSR(sem, polin, tam)
    except ValueError as erro:
        print(f"{rotulo}: ValueError: {erro}")

print("\nATAQUE — REÚSO DE KEYSTREAM (two-time pad)")
p1 = b"TRANSFERIR 1000 REAIS PARA A CONTA 12345"
p2 = b"TRANSFERIR 9999 REAIS PARA A CONTA 67890"
c1 = cifrar(p1, semente, POLINOMIO_16, 16)  # mesma semente
c2 = cifrar(p2, semente, POLINOMIO_16, 16)  # nas duas mensagens

xor_claros = ataque_reuso_de_chave(c1, c2)
print(f"c1 XOR c2 revela p1 XOR p2 sem a chave? {xor_claros == bytes(x ^ y for x, y in zip(p1, p2))}")

recuperado = bytes(x ^ y for x, y in zip(xor_claros, p1))
print(f"p2 recuperado a partir de p1: {recuperado.decode()}")

print("\nATAQUE — LINEARIDADE DO LFSR")
original = LFSR(0b1011, POLINOMIO_4, 4)
conhecidos = original.keystream_bits(4)

estado_recuperado = sum(bit << i for i, bit in enumerate(conhecidos))

clone = LFSR(estado_recuperado, POLINOMIO_4, 4)
clone.keystream_bits(4)  # avança o clone até o ponto em que o atacante entrou

print(f"Bits observados pelo atacante: {''.join(str(b) for b in conhecidos)}")
print(f"Semente real: {0b1011:04b} | reconstruída: {estado_recuperado:04b}")
print(f"Próximos 11 bits reais:  {''.join(str(b) for b in original.keystream_bits(11))}")
print(f"Previstos pelo clone:    {''.join(str(b) for b in clone.keystream_bits(11))}")
print("Conhecido o polinômio, o atacante prevê todo o keystream futuro.")