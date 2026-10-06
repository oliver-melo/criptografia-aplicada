from metodos_cifragem import hill

# Cifra de Hill: matriz classica invertivel no modulo 26
chave = [[3, 3], [2, 5]]
cifrado = hill("PARA", chave, True)

print("Hill cifrado:   ", cifrado)
print("Hill decifrado: ", hill(cifrado, chave, False))