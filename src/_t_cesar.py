from metodos_cifragem import cesar

# Cifra de Cesar
mensagem = "Ataque Amanha"
cifrado = cesar(mensagem, 3, True)
print("Cesar cifrado:  ", cifrado)
print("Cesar decifrado:", cesar(cifrado, 3, False))