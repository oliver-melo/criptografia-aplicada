from cifra_substituicao import cifrar, decifrar


chave = "QWERTYUIOPASDFGHJKLZXCVBNM"

texto = "TRANSFERIR DOCUMENTO PARA SERVIDOR CENTRAL"

cifrado = cifrar(texto, chave)
decifrado = decifrar(cifrado, chave)

print("Texto original:")
print(texto)

print("\nTexto cifrado:")
print(cifrado)

print("\nTexto decifrado:")
print(decifrado)