from metodos_cifragem import transposicao

texto = "TRANSFERIR DOCUMENTO PARA SERVIDOR CENTRAL"
chave = 5

cifrado = transposicao(texto, chave, True)
decifrado = transposicao(cifrado, chave, True)

print("texto original:")
print(texto)

print("\ntexto cifrado:")
print(cifrado)

print("\ntexto decifrado:")
print(decifrado)