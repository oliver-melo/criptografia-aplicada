from cifras_classicas import (
    ALFABETO_PADRAO,
    cifrar_afim,
    decifrar_afim,
    chaves_afim_validas,
    forca_bruta_afim,
    cifrar_vigenere,
    decifrar_vigenere,
    indice_de_coincidencia,
    estimar_tamanho_chave,
)

"""Testes das cifras clássicas: Afim e Vigenère"""

print("\nCIFRA AFIM — ida e volta")
mensagem = "SecureDocs e um sistema de documentos confidenciais"
a, b = 5, 8
cifrado = cifrar_afim(mensagem, a, b)
print(f"Claro:    {mensagem}")
print(f"Cifrado:  {cifrado}")
print(f"Decifrado:{decifrar_afim(cifrado, a, b)}")

print("\nCIFRA AFIM — acentuação e pontuação")
original = "Atenção: contrato nº 12 não assinado!"
c = cifrar_afim(original, 7, 3)
print(f"Claro:    {original}")
print(f"Cifrado:  {c}")
print(f"Decifrado:{decifrar_afim(c, 7, 3)}")

print("\nCIFRA AFIM — chave inválida (a não coprimo com 26)")
for chave_a in [2, 13, 26]:
    try:
        cifrar_afim("TESTE", chave_a, 1)
    except ValueError as erro:
        print(f"a={chave_a} -> ValueError: {erro}")

print("\nCIFRA AFIM — tamanho do espaço de chaves")
print(f"Chaves válidas no alfabeto de 26 letras: {chaves_afim_validas()}")  # 312
print("(phi(26)=12 opções para 'a' x 26 opções para 'b')")

print("\nCIFRA AFIM — ataque por força bruta")
alvo = cifrar_afim("ATAQUE AO AMANHECER", 11, 19)
print(f"Criptograma: {alvo}")
candidatos = forca_bruta_afim(alvo)
print(f"Total de tentativas: {len(candidatos)}")
achou = [(ca, cb, t) for ca, cb, t in candidatos if t.startswith("ATAQUE")]
print(f"Chave recuperada sem conhecimento prévio: {achou}")

print("\nVIGENERE — ida e volta")
mensagem = "Documento confidencial da TechSecure"
chave = "SECUREDOCS"
cifrado = cifrar_vigenere(mensagem, chave)
print(f"Claro:    {mensagem}")
print(f"Cifrado:  {cifrado}")
print(f"Decifrado:{decifrar_vigenere(cifrado, chave)}")

print("\nVIGENERE — a mesma letra vira letras diferentes")
print(f"AAAAA com chave CHAVE -> {cifrar_vigenere('AAAAA', 'CHAVE')}")
print("Monoalfabética (afim) devolveria a mesma letra cinco vezes:")
print(f"AAAAA com afim (5, 8) -> {cifrar_afim('AAAAA', 5, 8)}")

print("\nVIGENERE — chave de uma letra equivale à cifra de César")
print(f"Vigenere com chave 'D': {cifrar_vigenere('ATAQUE', 'D')}")
print(f"Afim com a=1, b=3:      {cifrar_afim('ATAQUE', 1, 3)}")

print("\nVIGENERE — chave vazia é rejeitada")
try:
    cifrar_vigenere("TESTE", "123!")
except ValueError as erro:
    print(f"ValueError: {erro}")

print("\nINDICE DE COINCIDENCIA")
texto_claro = (
    "a criptografia protege documentos confidenciais contra acesso nao autorizado "
    "e garante que a informacao transmitida permaneca integra durante todo o percurso "
    "entre o remetente e o destinatario final do sistema seguro de arquivos"
)
ic_claro = indice_de_coincidencia(texto_claro)
ic_vigenere = indice_de_coincidencia(cifrar_vigenere(texto_claro, "CHAVE"))
ic_afim = indice_de_coincidencia(cifrar_afim(texto_claro, 5, 8))
print(f"IC do texto claro:            {ic_claro:.4f}  (português ~0.072)")
print(f"IC após Vigenère (chave 5):   {ic_vigenere:.4f}  (achata em direção a 0.038)")
print(f"IC após Afim:                 {ic_afim:.4f}  (inalterado: só permuta letras)")

print("\nESTIMATIVA DO TAMANHO DA CHAVE DE VIGENERE")
# Texto longo o bastante para a estatística funcionar
longo = texto_claro * 6
criptograma = cifrar_vigenere(longo, "SEGURO")  # chave de 6 letras
ranking = estimar_tamanho_chave(criptograma, limite=12)
print("Tamanhos mais prováveis (tamanho, IC médio):")
for tamanho, ic in ranking[:4]:
    print(f"  t = {tamanho:2d} -> {ic:.4f}")
print("A chave real tem 6 letras — múltiplos de 6 também pontuam alto.")