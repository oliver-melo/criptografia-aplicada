from metodos_cifragem import vigenere, ALFABETO, indice_de_coincidencia, estimar_tamanho_chave 

print("\nVIGENERE — ida e volta")
mensagem = "Documento confidencial da TechSecure"
chave = "SECUREDOCS"
cifrado = vigenere(mensagem, chave, True)
print(f"Claro:    {mensagem}")
print(f"Cifrado:  {cifrado}")
print(f"Decifrado:{vigenere(cifrado, chave, False)}")

print("\nVIGENERE — a mesma letra vira letras diferentes")
print(f"AAAAA com chave CHAVE -> {vigenere('AAAAA', 'CHAVE', True)}")

print("\nVIGENERE — chave de uma letra equivale à cifra de César")
print(f"Vigenere com chave 'D': {vigenere('ATAQUE', 'D', True)}")

print("\nVIGENERE — chave vazia é rejeitada")
try:
    vigenere("TESTE", "123!", True)
except ValueError as erro:
    print(f"ValueError: {erro}")

print("\nINDICE DE COINCIDENCIA")
texto_claro = (
    "a criptografia protege documentos confidenciais contra acesso nao autorizado "
    "e garante que a informacao transmitida permaneca integra durante todo o percurso "
    "entre o remetente e o destinatario final do sistema seguro de arquivos"
)

ic_claro = indice_de_coincidencia(texto_claro)
ic_vigenere = indice_de_coincidencia(vigenere(texto_claro, "CHAVE", True))
print(f"IC do texto claro:            {ic_claro:.4f}  (português ~0.072)")
print(f"IC após Vigenère (chave 5):   {ic_vigenere:.4f}  (achata em direção a 0.038)")

print("\nESTIMATIVA DO TAMANHO DA CHAVE DE VIGENERE")
# Texto longo o bastante para a estatística funcionar
longo = texto_claro * 6
criptograma = vigenere(longo, "SEGURO", True)  # chave de 6 letras
ranking = estimar_tamanho_chave(criptograma, limite=12)
print("Tamanhos mais prováveis (tamanho, IC médio):")
for tamanho, ic in ranking[:4]:
    print(f"  t = {tamanho:2d} -> {ic:.4f}")
print("A chave real tem 6 letras — múltiplos de 6 também pontuam alto.")