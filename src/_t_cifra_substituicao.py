from metodos_cifragem import substituicao

chave = "QWERTYUIOPASDFGHJKLZXCVBNM"

texto = "TRANSFERIR DOCUMENTO PARA SERVIDOR CENTRAL"

cifrado = substituicao(texto, chave, True)
decifrado = substituicao(cifrado, chave, False)

print("Texto original:")
print(texto)

print("\nTexto cifrado:")
print(cifrado)

print("\nTexto decifrado:")
print(decifrado)