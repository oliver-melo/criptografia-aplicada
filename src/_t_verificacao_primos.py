from verificacao_primos import VerificaPrimos

"""Testes unitários para a classe VerificaPrimos"""

print("Método simples")
print(VerificaPrimos.simples(2))  # True
print(VerificaPrimos.simples(3))  # True
print(VerificaPrimos.simples(4))  # False
print(VerificaPrimos.simples(5))  # True
print(VerificaPrimos.simples(16))  # False
print(VerificaPrimos.simples(17))  # True

print("\nMétodo Miller-Rabin")
k = 40  # Número de rodadas de teste
print(VerificaPrimos.miller_rabin(7919, k))  # True
print(VerificaPrimos.miller_rabin(6389, k))  # True
print(VerificaPrimos.miller_rabin(97686, k))  # False
print(VerificaPrimos.miller_rabin(293, k))  # True
print(VerificaPrimos.miller_rabin(7855, k))  # False
print(VerificaPrimos.miller_rabin(17, k))  # True

