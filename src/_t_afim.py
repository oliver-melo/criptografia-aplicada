from metodos_cifragem import afim, vigenere, ALFABETO, _normalizar, indice_de_coincidencia, estimar_tamanho_chave 
from algoritmos_fundamentais import is_coprime, totiente_euler

"""funcoes auxiliares para teste de cifra afim"""

def forca_bruta_afim(texto: str, alfabeto: str = ALFABETO) -> list[tuple[int, int, str]]:
    """
    Ataque por força bruta: devolve (a, b, texto_decifrado) para toda
    chave válida.

    """

    m = len(alfabeto)
    tentativas = []

    for a in range(1, m):
        if not is_coprime(a, m):
            continue
        for b in range(m):
            tentativas.append((a, b, afim(texto, a, b, False)))

    return tentativas

def chaves_afim_validas(alfabeto: str = ALFABETO) -> int:
    m = len(alfabeto)
    return totiente_euler(m) * m

"""inicio dos testes da cifra afim"""

print("\nCIFRA AFIM — ida e volta")
mensagem = "SecureDocs e um sistema de documentos confidenciais"
a, b = 5, 8
cifrado = afim(mensagem, a, b, True)
print(f"Claro:    {mensagem}")
print(f"Cifrado:  {cifrado}")
print(f"Decifrado:{afim(cifrado, a, b, False)}")

print("\nCIFRA AFIM — acentuação e pontuação")
original = "Atenção: contrato nº 12 não assinado!"
c = afim(original, 7, 3, True)
print(f"Claro:    {original}")
print(f"Cifrado:  {c}")
print(f"Decifrado:{afim(c, 7, 3, False)}")

print("\nCIFRA AFIM — chave inválida (a não coprimo com 26)")
for chave_a in [2, 13, 26]:
    try:
        afim("TESTE", chave_a, 1, True)
    except ValueError as erro:
        print(f"a={chave_a} -> ValueError: {erro}")

print("\nCIFRA AFIM — tamanho do espaço de chaves")
print(f"Chaves válidas no alfabeto de 26 letras: {chaves_afim_validas()}")  # 312
print("(phi(26)=12 opções para 'a' x 26 opções para 'b')")

print("\nCIFRA AFIM — ataque por força bruta")
alvo = afim("ATAQUE AO AMANHECER", 11, 19, True)
print(f"Criptograma: {alvo}")
candidatos = forca_bruta_afim(alvo)
print(f"Total de tentativas: {len(candidatos)}")
achou = [(ca, cb, t) for ca, cb, t in candidatos if t.startswith("ATAQUE")]
print(f"Chave recuperada sem conhecimento prévio: {achou}")

print("\nINDICE DE COINCIDENCIA")
texto_claro = (
    "a criptografia protege documentos confidenciais contra acesso nao autorizado "
    "e garante que a informacao transmitida permaneca integra durante todo o percurso "
    "entre o remetente e o destinatario final do sistema seguro de arquivos"
)

ic_claro = indice_de_coincidencia(texto_claro)
ic_afim = indice_de_coincidencia(afim(texto_claro, 5, 8, True))
print(f"IC do texto claro:            {ic_claro:.4f}  (português ~0.072)")
print(f"IC após Afim:                 {ic_afim:.4f}  (inalterado: só permuta letras)")