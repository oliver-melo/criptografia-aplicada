from numero_modular import NumeroModular
from algoritmos_fundamentais import is_coprime

def teorema_chines_do_resto(equacoes: list[NumeroModular]) -> NumeroModular:
    """
    equacoes: Uma lista de objetos NumeroModular representando as congruências 
              do tipo x ≡ num (mod m),
              onde m é o módulo de cada equação. 
                  
    Returns:
        Um objeto NumeroModular representando a solução x (mod M), 
        onde M é o produto de todos os módulos (m) do sistema.
    """

    tamanho = len(equacoes)
    
    # 1. Verificar se todos os módulos são coprimos entre si a pares
    for i in range(tamanho):
        for j in range(i + 1, tamanho):
            if not is_coprime(equacoes[i].mod, equacoes[j].mod):
                raise ValueError(
                    f"Os módulos {equacoes[i].mod} e {equacoes[j].mod} não são coprimos. "
                    "O teorema exige que os módulos sejam coprimos."
                )
    
    # 2. Calcular o M (produto de todos os módulos)
    M = 1
    for eq in equacoes:
        M *= eq.mod
        
    # 3. Calcular a solução (somatório de a_i * M_i * y_i)
    x_total = 0
    for eq in equacoes:
        a_i = eq.num_mod
        m_i = eq.mod
        
        # M_i é o produto de todos os módulos, exceto o módulo atual (m_i)
        M_i = M // m_i
        
        # Transforma M_i em NumeroModular para encontrar seu inverso mod m_i
        num_M_i = NumeroModular(M_i, m_i)
        y_i_modular = num_M_i.inverso_multiplicativo()
        
        if y_i_modular is None:
            raise ValueError(f"Inverso multiplicativo não encontrado para {M_i} mod {m_i}.")
            
        y_i = y_i_modular.num_mod
        
        # Somar o termo ao x_total
        x_total += a_i * M_i * y_i
        
    # 4. Retornar a solução já encapsulada na classe, que aplicará o módulo M automaticamente
    return NumeroModular(x_total, M)