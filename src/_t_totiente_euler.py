from algoritmos_fundamentais import (
    fatoracao_prima,
    totiente_euler,
    totiente_euler_ingenuo,
    is_prime,
)
from numero_modular import NumeroModular as nMod

"""Testes da função φ (totiente) de Euler"""

print("\nFATORAÇÃO PRIMA")
print(f"36  = {fatoracao_prima(36)}")   # {2: 2, 3: 2}
print(f"97  = {fatoracao_prima(97)}")   # {97: 1}
print(f"360 = {fatoracao_prima(360)}")  # {2: 3, 3: 2, 5: 1}

print("\nVALORES DE φ(n)")
for n in [1, 2, 9, 10, 12, 36, 97, 100]:
    print(f"φ({n}) = {totiente_euler(n)}")
# φ(1)=1, φ(2)=1, φ(9)=6, φ(10)=4, φ(12)=4, φ(36)=12, φ(97)=96, φ(100)=40

print("\nPROPRIEDADE: se p é primo, φ(p) = p - 1")
for p in [2, 7, 13, 97, 7919]:
    ok = is_prime(p) and totiente_euler(p) == p - 1
    print(f"p = {p}: φ(p) = {totiente_euler(p)} = p - 1? {'Sim' if ok else 'Não'}")

print("\nPROPRIEDADE: φ(p*q) = (p-1)*(q-1) para p, q primos distintos (base do RSA)")
p, q = 61, 53
n = p * q
print(f"p = {p}, q = {q}, n = {n}")
print(f"φ({n}) = {totiente_euler(n)} | (p-1)*(q-1) = {(p - 1) * (q - 1)}")

print("\nPROPRIEDADE: φ é multiplicativa para argumentos coprimos — φ(a*b) = φ(a)*φ(b)")
a, b = 8, 9  # mdc(8, 9) = 1
print(f"φ({a}*{b}) = {totiente_euler(a * b)} | φ({a})*φ({b}) = {totiente_euler(a) * totiente_euler(b)}")

print("\nVALIDAÇÃO CRUZADA: fórmula por fatoração x contagem direta")
divergencias = [n for n in range(1, 501) if totiente_euler(n) != totiente_euler_ingenuo(n)]
print(f"Divergências em [1, 500]: {len(divergencias)}")  # 0

print("\nTEOREMA DE EULER: a^φ(n) ≡ 1 (mod n), para mdc(a, n) = 1")
for num, mod in [(5, 12), (3, 10), (7, 36), (2, 97)]:
    a = nMod(num, mod)
    phi = totiente_euler(mod)
    print(f"{a} ^ φ({mod})={phi}  ->  {(a ** phi).num_mod}")  # sempre 1

print("\nCASOS INVÁLIDOS")
for valor in [0, -5, 3.5]:
    try:
        totiente_euler(valor)
    except ValueError as erro:
        print(f"φ({valor}) -> ValueError: {erro}")