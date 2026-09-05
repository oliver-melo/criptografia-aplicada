from aritmetica_modular import NumeroModular as nMod 

mod = 7

a = nMod(5, mod)
b = nMod(3, mod)

print(f"\nValores: a = {a.num_mod} (mod {a.mod}), b = {b.num_mod} (mod {b.mod})")

print("\nTESTE DE ARITMÉTICA MODULAR")

soma = a + b
print(f"\nSOMA: {a} + {b} = {soma}")  # Saída: 5 + 3 = 1

sub = a - b
print(f"SUBTRAÇÃO: {a} - {b} = {sub}")  # Saída: 5 - 3 = 2

mul = a * b
print(f"MULTIPLICAÇÃO: {a} * {b} = {mul}")  # Saída: 5 * 3 = 1

inverso_b = b.inverso_multiplicativo()
if inverso_b is not None:
    print(f"INVERSO MULTIPLICATIVO: {b} -¹ = {inverso_b}")  # Saída: O inverso multiplicativo de 3 (mod 7) é: 5 (mod 7)

mul_inverso = a * inverso_b
print(f"MULTIPLICAÇÃO PELO INVERSO: {a} * {inverso_b} = {mul_inverso}")

div = a / b
print(f"DIVISÃO: {a} / {b} = {div}")  # Saída: 5 / 3 = 4

print(f"\ndivisão {div} = multiplicação pelo inverso {mul_inverso}") if div == mul_inverso else print("As operações não coincidem.")

print("\nTESTE DE CONGRUÊNCIA E IGUALDADE")

c = nMod(10, mod)
d = nMod(24, mod)
e = nMod(15, mod)
print(f"Valores: c = {c.num} (mod {c.mod}), d = {d.num} (mod {d.mod}), e = {e.num} (mod {e.mod})")

print(f"{c} é congruente a {d}? {'Sim' if c.congruente(d) else 'Não'}")  # Saída: 10 é congruente a 24? Sim
print(f"{c} é igual a {d}? {'Sim' if c==d else 'Não'}")  # Saída: 10 é igual a 24? Não
print(f"{c} é congruente a {e}? {'Sim' if c.congruente(e) else 'Não'}")  # Saída: 10 é congruente a 15? Nao
print(f"{d} é congruente a {e}? {'Sim' if d.congruente(e) else 'Não'}")  # Saída: 24 é congruente a 15? Nao