from cifras import cifrar_cesar, cifrar_hill, decifrar_cesar, decifrar_hill


# Cifra de Cesar
mensagem = "Ataque Amanha"
cesar = cifrar_cesar(mensagem, 3)
print("Cesar cifrado:  ", cesar)
print("Cesar decifrado:", decifrar_cesar(cesar, 3))

# Cifra de Hill: matriz classica invertivel no modulo 26
chave = [[3, 3], [2, 5]]
hill = cifrar_hill("PARA", chave)
print("Hill cifrado:   ", hill)
print("Hill decifrado: ", decifrar_hill(hill, chave))
