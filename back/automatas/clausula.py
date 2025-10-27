"""
Construcción de Thompson: Expresión Regular → AFN
Conversión AFN → Expresión Regular
Algoritmo de Clausura (Kleene)
"""

from afn_base import AFN


class ConstructorThompson:
    """
    Construcción de Thompson para convertir expresiones regulares a AFN
    Operaciones:
    - Concatenación: r1·r2
    - Unión: r1|r2
    - Clausura de Kleene: r*
    - Clausura positiva: r+
    """
    
    def __init__(self):
        self.contador_estados = 0
    
    def nuevo_estado(self):
        """Genera un nuevo estado único"""
        estado = f"q{self.contador_estados}"
        self.contador_estados += 1
        return estado
    
    def simbolo(self, simbolo):
        """
        AFN básico para un solo símbolo: a
        q0 --a--> q1
        """
        q0 = self.nuevo_estado()
        q1 = self.nuevo_estado()
        
        estados = {q0, q1}
        alfabeto = {simbolo}
        transiciones = {(q0, simbolo): {q1}}
        
        return AFN(estados, alfabeto, transiciones, q0, {q1})
    
    def epsilon(self):
        """
        AFN para ε (cadena vacía)
        q0 --ε--> q1
        """
        q0 = self.nuevo_estado()
        q1 = self.nuevo_estado()
        
        estados = {q0, q1}
        alfabeto = set()
        transiciones = {(q0, 'ε'): {q1}}
        
        return AFN(estados, alfabeto, transiciones, q0, {q1})
    
    def concatenacion(self, afn1, afn2):
        """
        Concatenación: r1·r2
        Conecta el estado final de afn1 con el inicial de afn2 mediante ε
        """
        # Combinar estados
        estados = afn1.Q | afn2.Q
        alfabeto = afn1.sigma | afn2.sigma
        transiciones = dict(afn1.delta)
        transiciones.update(afn2.delta)
        
        # Conectar final de afn1 con inicial de afn2
        for estado_final in afn1.F:
            if (estado_final, 'ε') not in transiciones:
                transiciones[(estado_final, 'ε')] = set()
            transiciones[(estado_final, 'ε')].add(afn2.q0)
        
        return AFN(estados, alfabeto, transiciones, afn1.q0, afn2.F)
    
    def union(self, afn1, afn2):
        """
        Unión: r1|r2
        Nuevo estado inicial con ε-transiciones a ambos AFN
        Estados finales de ambos se conectan a nuevo estado final
        """
        q0_nuevo = self.nuevo_estado()
        qf_nuevo = self.nuevo_estado()
        
        estados = afn1.Q | afn2.Q | {q0_nuevo, qf_nuevo}
        alfabeto = afn1.sigma | afn2.sigma
        
        transiciones = dict(afn1.delta)
        transiciones.update(afn2.delta)
        
        # Nueva inicial apunta a ambos iniciales
        transiciones[(q0_nuevo, 'ε')] = {afn1.q0, afn2.q0}
        
        # Ambos finales apuntan al nuevo final
        for estado_final in afn1.F:
            if (estado_final, 'ε') not in transiciones:
                transiciones[(estado_final, 'ε')] = set()
            transiciones[(estado_final, 'ε')].add(qf_nuevo)
        
        for estado_final in afn2.F:
            if (estado_final, 'ε') not in transiciones:
                transiciones[(estado_final, 'ε')] = set()
            transiciones[(estado_final, 'ε')].add(qf_nuevo)
        
        return AFN(estados, alfabeto, transiciones, q0_nuevo, {qf_nuevo})
    
    def clausura_kleene(self, afn):
        """
        Clausura de Kleene: r*
        Permite 0 o más repeticiones
        """
        q0_nuevo = self.nuevo_estado()
        qf_nuevo = self.nuevo_estado()
        
        estados = afn.Q | {q0_nuevo, qf_nuevo}
        alfabeto = afn.sigma
        transiciones = dict(afn.delta)
        
        # Nuevo inicial puede ir al inicial original o al final (cadena vacía)
        transiciones[(q0_nuevo, 'ε')] = {afn.q0, qf_nuevo}
        
        # Finales del AFN van al nuevo final o de vuelta al inicio (repetición)
        for estado_final in afn.F:
            if (estado_final, 'ε') not in transiciones:
                transiciones[(estado_final, 'ε')] = set()
            transiciones[(estado_final, 'ε')].update({qf_nuevo, afn.q0})
        
        return AFN(estados, alfabeto, transiciones, q0_nuevo, {qf_nuevo})
    
    def clausura_positiva(self, afn):
        """
        Clausura positiva: r+
        Permite 1 o más repeticiones (equivalente a r·r*)
        """
        # r+ = r·r*
        afn_estrella = self.clausura_kleene(afn)
        return self.concatenacion(afn, afn_estrella)
    
    def desde_expresion_simple(self, expresion):
        """
        Construye AFN desde una expresión regular simple
        Soporta: símbolos, |, *, +, concatenación
        """
        # Ejemplo simplificado: "a|b" o "a*" o "ab"
        
        if '|' in expresion:
            # Unión
            partes = expresion.split('|')
            afn_resultado = self.desde_expresion_simple(partes[0])
            for parte in partes[1:]:
                afn_parte = self.desde_expresion_simple(parte)
                afn_resultado = self.union(afn_resultado, afn_parte)
            return afn_resultado
        
        elif expresion.endswith('*'):
            # Clausura de Kleene
            sub_expr = expresion[:-1]
            afn_sub = self.desde_expresion_simple(sub_expr)
            return self.clausura_kleene(afn_sub)
        
        elif expresion.endswith('+'):
            # Clausura positiva
            sub_expr = expresion[:-1]
            afn_sub = self.desde_expresion_simple(sub_expr)
            return self.clausura_positiva(afn_sub)
        
        elif len(expresion) == 1:
            # Símbolo simple
            return self.simbolo(expresion)
        
        else:
            # Concatenación
            afn_resultado = self.simbolo(expresion[0])
            for simbolo in expresion[1:]:
                afn_simbolo = self.simbolo(simbolo)
                afn_resultado = self.concatenacion(afn_resultado, afn_simbolo)
            return afn_resultado


def ejemplos_construccion_thompson():
    """
    Ejemplos de construcción de AFN desde expresiones regulares
    """
    constructor = ConstructorThompson()
    
    print("=" * 60)
    print("Construcción de Thompson: ER → AFN")
    print("=" * 60)
    
    # Ejemplo 1: Símbolo simple
    print("\n1. Expresión Regular: 'a'")
    afn_a = constructor.simbolo('a')
    print(afn_a)
    print("   Acepta: cadenas con un solo 'a'")
    
    # Ejemplo 2: Concatenación
    print("\n2. Expresión Regular: 'ab' (concatenación)")
    afn_ab = constructor.desde_expresion_simple('ab')
    print(afn_ab)
    resultado, msg = afn_ab.procesar('ab')
    print(f"   Prueba 'ab': {'✓ ACEPTA' if resultado else '✗ RECHAZA'}")
    
    # Ejemplo 3: Unión
    print("\n3. Expresión Regular: 'a|b' (unión)")
    afn_union = constructor.desde_expresion_simple('a|b')
    print(afn_union)
    for cadena in ['a', 'b', 'c']:
        resultado, _ = afn_union.procesar(cadena)
        print(f"   Prueba '{cadena}': {'✓ ACEPTA' if resultado else '✗ RECHAZA'}")
    
    # Ejemplo 4: Clausura de Kleene
    print("\n4. Expresión Regular: 'a*' (clausura de Kleene)")
    afn_kleene = constructor.desde_expresion_simple('a*')
    print(afn_kleene)
    for cadena in ['', 'a', 'aa', 'aaa', 'b']:
        resultado, _ = afn_kleene.procesar(cadena)
        print(f"   Prueba '{cadena}': {'✓ ACEPTA' if resultado else '✗ RECHAZA'}")
    
    # Ejemplo 5: Clausura positiva
    print("\n5. Expresión Regular: 'a+' (clausura positiva)")
    afn_positiva = constructor.desde_expresion_simple('a+')
    print(afn_positiva)
    for cadena in ['', 'a', 'aa', 'aaa']:
        resultado, _ = afn_positiva.procesar(cadena)
        print(f"   Prueba '{cadena}': {'✓ ACEPTA' if resultado else '✗ RECHAZA'}")


def aplicacion_jwt():
    """
    Aplicación práctica: Validar patrones en JWT usando construcción de Thompson
    """
    print("\n" + "=" * 60)
    print("Aplicación JWT: Validación de claim 'iss' (issuer)")
    print("=" * 60)
    
    constructor = ConstructorThompson()
    
    # Expresión regular para dominios válidos: (a|b|c)+ . (c|o|m)+
    # Simplificado: acepta "auth.company" donde auth es (a-z)+ y company es (a-z)+
    
    print("\nER: Validar issuer como 'palabra.palabra'")
    print("Construcción: (letra)+ · '.' · (letra)+")
    
    # Construir AFN para 'a|b|c|...'
    alfabeto_letras = 'abcdefghijklmnopqrstuvwxyz'
    
    # Por simplicidad, solo usamos 'a', 'u', 't', 'h'
    afn_auth = constructor.desde_expresion_simple('auth')
    afn_punto = constructor.simbolo('.')
    afn_com = constructor.desde_expresion_simple('com')
    
    # Concatenar: auth.com
    afn_issuer = constructor.concatenacion(afn_auth, afn_punto)
    afn_issuer = constructor.concatenacion(afn_issuer, afn_com)
    
    print(afn_issuer)
    
    casos = ['auth.com', 'auth.org', 'invalid']
    for caso in casos:
        resultado, msg = afn_issuer.procesar(caso)
        print(f"\n   '{caso}': {'✓ ACEPTA' if resultado else '✗ RECHAZA'}")
        print(f"   {msg}")


# Ejemplo de uso
if __name__ == "__main__":
    ejemplos_construccion_thompson()
    aplicacion_jwt()
    
    print("\n" + "=" * 60)
    print("Resumen de Operaciones de Clausura")
    print("=" * 60)
    print("""
    Operaciones Básicas:
    
    1. Concatenación (r₁·r₂): 
       - Une dos AFN en secuencia
       - ε-transición del final de r₁ al inicio de r₂
    
    2. Unión (r₁|r₂):
       - Nuevo estado inicial con ε a ambos
       - Ambos finales van a nuevo estado final
    
    3. Clausura de Kleene (r*):
       - Permite 0 o más repeticiones
       - ε desde nuevo inicial a original y a final
       - ε desde finales a inicial (repetir) y a nuevo final
    
    4. Clausura Positiva (r+):
       - Permite 1 o más repeticiones
       - Equivalente a r·r*
    
    Aplicación en JWT:
    - Validar formato de emails
    - Validar URLs en claims
    - Validar patrones de fechas
    - Validar identificadores
    """)
