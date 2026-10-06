from cifra_transposicao import cifrar, decifrar

texto = "TRANSFERIR DOCUMENTO PARA SERVIDOR CENTRAL"
chave = 5

cifrado = cifrar(texto, chave)
decifrado = decifrar(cifrado, chave)

print("texto original:")
print(texto)

print("\ntexto cifrado:")
print(cifrado)

print("\ntexto decifrado:")
print(decifrado)