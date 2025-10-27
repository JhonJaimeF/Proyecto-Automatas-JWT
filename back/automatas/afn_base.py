"""
Implementación de Autómata Finito No Determinista (AFN)
Aplicado a la validación de patrones en JWT
"""

class AFN:
    """
    Autómata Finito No Determinista (Q, Σ, δ, q0, F)
    Permite múltiples transiciones y transiciones epsilon (ε)
    """
    
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_finales):
        self.Q = estados
        self.sigma = alfabeto
        self.delta = transiciones  # δ(q, a) -> {q1, q2, ...} (conjunto de estados)
        self.q0 = estado_inicial
        self.F = estados_finales
        self.epsilon = 'ε'  # Símbolo epsilon
    
    def epsilon_clausura(self, estados):
        """
        Calcula la ε-clausura de un conjunto de estados
        Incluye todos los estados alcanzables mediante transiciones ε
        """
        clausura = set(estados)
        pila = list(estados)
        
        while pila:
            estado = pila.pop()
            # Buscar transiciones epsilon desde este estado
            if (estado, self.epsilon) in self.delta:
                for siguiente in self.delta[(estado, self.epsilon)]:
                    if siguiente not in clausura:
                        clausura.add(siguiente)
                        pila.append(siguiente)
        
        return clausura
    
    def mover(self, estados, simbolo):
        """
        Calcula el conjunto de estados alcanzables desde 'estados' con 'simbolo'
        """
        resultado = set()
        for estado in estados:
            if (estado, simbolo) in self.delta:
                resultado.update(self.delta[(estado, simbolo)])
        return resultado
    
    def procesar(self, cadena):
        """
        Procesa una cadena usando el AFN
        Retorna True si la cadena es aceptada
        """
        # Comenzar con la ε-clausura del estado inicial
        estados_actuales = self.epsilon_clausura({self.q0})
        
        for i, simbolo in enumerate(cadena):
            # Verificar si el símbolo está en el alfabeto
            if simbolo not in self.sigma and simbolo != self.epsilon:
                return False, f"Símbolo '{simbolo}' no válido en posición {i}"
            
            # Calcular nuevos estados
            nuevos_estados = self.mover(estados_actuales, simbolo)
            estados_actuales = self.epsilon_clausura(nuevos_estados)
            
            if not estados_actuales:
                return False, f"No hay transiciones posibles desde posición {i}"
        
        # Verificar si algún estado actual es final
        if estados_actuales & self.F:
            return True, f"Cadena aceptada. Estados finales alcanzados: {estados_actuales & self.F}"
        else:
            return False, f"Cadena rechazada. Estados actuales: {estados_actuales}"
    
    def __str__(self):
        return f"""
AFN:
  Estados (Q): {self.Q}
  Alfabeto (Σ): {self.sigma}
  Estado inicial (q0): {self.q0}
  Estados finales (F): {self.F}
  Transiciones (δ): {len(self.delta)} transiciones
"""


def crear_afn_timestamp_formats():
    """
    AFN que acepta múltiples formatos de timestamp en claims:
    - Formato Unix: dígitos puros (1234567890)
    - Formato ISO: YYYY-MM-DD (con separadores)
    
    Este AFN demuestra no-determinismo: desde el estado inicial
    puede tomar diferentes caminos según el formato
    """
    
    estados = {'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7'}
    alfabeto = set('0123456789-')
    
    transiciones = {}
    
    # Rama 1: Timestamp Unix (solo dígitos)
    # q0 --ε--> q1 (decisión no-determinista)
    transiciones[('q0', 'ε')] = {'q1'}
    
    # q1: acepta dígitos (timestamp Unix)
    for digit in '0123456789':
        if ('q1', digit) not in transiciones:
            transiciones[('q1', digit)] = set()
        transiciones[('q1', digit)].add('q1')
    
    # Rama 2: Formato ISO (YYYY-MM-DD)
    # q0 --ε--> q2 (decisión no-determinista)
    if ('q0', 'ε') not in transiciones:
        transiciones[('q0', 'ε')] = set()
    transiciones[('q0', 'ε')].add('q2')
    
    # q2-q3: Leer 4 dígitos (año)
    for digit in '0123456789':
        transiciones[('q2', digit)] = {'q3'}
        transiciones[('q3', digit)] = {'q4'}
        transiciones[('q4', digit)] = {'q5'}
        transiciones[('q5', digit)] = {'q6'}
    
    # q6: Leer guión
    transiciones[('q6', '-')] = {'q7'}
    
    # Continuar con mes y día...
    # (simplificado para demostración)
    
    estados_finales = {'q1', 'q7'}  # Ambos formatos son válidos
    
    return AFN(estados, alfabeto, transiciones, 'q0', estados_finales)


def crear_afn_email_pattern():
    """
    AFN que valida patrones de email en claims (simplificado)
    user@domain
    
    Demuestra uso de ε-transiciones
    """
    estados = {'q0', 'q1', 'q2', 'q3', 'q4'}
    alfabeto = set('abcdefghijklmnopqrstuvwxyz0123456789@.')
    
    transiciones = {}
    
    # Estado q0: leer parte local (antes de @)
    for c in alfabeto - {'@', '.'}:
        if ('q0', c) not in transiciones:
            transiciones[('q0', c)] = set()
        transiciones[('q0', c)].add('q1')
        
        if ('q1', c) not in transiciones:
            transiciones[('q1', c)] = set()
        transiciones[('q1', c)].add('q1')
    
    # @ obligatorio
    transiciones[('q1', '@')] = {'q2'}
    
    # Dominio
    for c in alfabeto - {'@', '.'}:
        if ('q2', c) not in transiciones:
            transiciones[('q2', c)] = set()
        transiciones[('q2', c)].add('q3')
        
        if ('q3', c) not in transiciones:
            transiciones[('q3', c)] = set()
        transiciones[('q3', c)].add('q3')
    
    # Punto antes de TLD
    transiciones[('q3', '.')] = {'q4'}
    
    # TLD
    for c in alfabeto - {'@', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}:
        if ('q4', c) not in transiciones:
            transiciones[('q4', c)] = set()
        transiciones[('q4', c)].add('q4')
    
    return AFN(estados, alfabeto, transiciones, 'q0', {'q4'})


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("AFN para validación de formatos de timestamp")
    print("=" * 60)
    
    afn_timestamp = crear_afn_timestamp_formats()
    print(afn_timestamp)
    
    casos_timestamp = [
        "1234567890",  # Unix timestamp
        "2025-10-23",  # ISO format (simplificado)
    ]
    
    print("\nPruebas de timestamps:\n")
    for i, caso in enumerate(casos_timestamp, 1):
        aceptado, mensaje = afn_timestamp.procesar(caso)
        print(f"{i}. '{caso}'")
        print(f"   {'✓ ACEPTADO' if aceptado else '✗ RECHAZADO'}: {mensaje}\n")
    
    print("\n" + "=" * 60)
    print("AFN para validación de email en claims")
    print("=" * 60)
    
    afn_email = crear_afn_email_pattern()
    
    casos_email = [
        "user@example.com",
        "admin@company.org",
        "invalid.email",
        "@nodomain.com",
    ]
    
    print("\nPruebas de emails:\n")
    for i, caso in enumerate(casos_email, 1):
        aceptado, mensaje = afn_email.procesar(caso)
        print(f"{i}. '{caso}'")
        print(f"   {'✓ ACEPTADO' if aceptado else '✗ RECHAZADO'}: {mensaje}\n")
