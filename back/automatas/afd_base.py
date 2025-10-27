"""
Implementación de Autómata Finito Determinista (AFD)
Aplicado a la validación de JWT
"""

class AFD:
    """
    Autómata Finito Determinista (Q, Σ, δ, q0, F)
    Q: Conjunto de estados
    Σ: Alfabeto
    δ: Función de transición
    q0: Estado inicial
    F: Estados finales
    """
    
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_finales):
        self.Q = estados  # Conjunto de estados
        self.sigma = alfabeto  # Alfabeto
        self.delta = transiciones  # Función de transición δ(q, a) -> q'
        self.q0 = estado_inicial  # Estado inicial
        self.F = estados_finales  # Estados finales (aceptación)
        
    def procesar(self, cadena):
        """
        Procesa una cadena y retorna si es aceptada por el AFD
        """
        estado_actual = self.q0
        
        for i, simbolo in enumerate(cadena):
            # Verificar si el símbolo está en el alfabeto
            if simbolo not in self.sigma:
                return False, f"Símbolo '{simbolo}' no válido en posición {i}"
            
            # Obtener siguiente estado
            clave = (estado_actual, simbolo)
            if clave not in self.delta:
                return False, f"No hay transición desde estado '{estado_actual}' con símbolo '{simbolo}'"
            
            estado_actual = self.delta[clave]
        
        # Verificar si terminamos en un estado final
        if estado_actual in self.F:
            return True, f"Cadena aceptada. Estado final: {estado_actual}"
        else:
            return False, f"Cadena rechazada. Estado actual '{estado_actual}' no es final"
    
    def es_determinista(self):
        """
        Verifica que sea determinista (máximo una transición por (estado, símbolo))
        """
        for estado in self.Q:
            for simbolo in self.sigma:
                transiciones = [(e, s) for (e, s) in self.delta.keys() if e == estado and s == simbolo]
                if len(transiciones) > 1:
                    return False
        return True
    
    def __str__(self):
        return f"""
AFD:
  Estados (Q): {self.Q}
  Alfabeto (Σ): {self.sigma}
  Estado inicial (q0): {self.q0}
  Estados finales (F): {self.F}
  Transiciones (δ): {len(self.delta)} transiciones
"""


def crear_afd_jwt_estructura():
    """
    Crea un AFD que valida la estructura básica de un JWT:
    header.payload.signature
    
    Estados:
    - q0: Inicial (esperando header)
    - q1: Leyendo header
    - q2: Primer punto leído (esperando payload)
    - q3: Leyendo payload
    - q4: Segundo punto leído (esperando signature)
    - q5: Leyendo signature
    - q6: Final (JWT válido)
    """
    
    estados = {'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6'}
    
    # Alfabeto: caracteres válidos en Base64URL + punto
    # Base64URL: A-Z, a-z, 0-9, -, _
    alfabeto = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.')
    
    transiciones = {}
    
    # Transiciones desde q0 (inicial)
    for c in alfabeto - {'.'}:
        transiciones[('q0', c)] = 'q1'  # Comenzar a leer header
    
    # Transiciones desde q1 (leyendo header)
    for c in alfabeto - {'.'}:
        transiciones[('q1', c)] = 'q1'  # Continuar leyendo header
    transiciones[('q1', '.')] = 'q2'  # Primer punto
    
    # Transiciones desde q2 (después del primer punto)
    for c in alfabeto - {'.'}:
        transiciones[('q2', c)] = 'q3'  # Comenzar a leer payload
    
    # Transiciones desde q3 (leyendo payload)
    for c in alfabeto - {'.'}:
        transiciones[('q3', c)] = 'q3'  # Continuar leyendo payload
    transiciones[('q3', '.')] = 'q4'  # Segundo punto
    
    # Transiciones desde q4 (después del segundo punto)
    for c in alfabeto - {'.'}:
        transiciones[('q4', c)] = 'q5'  # Comenzar a leer signature
    
    # Transiciones desde q5 (leyendo signature)
    for c in alfabeto - {'.'}:
        transiciones[('q5', c)] = 'q5'  # Continuar leyendo signature
    
    # Estado final alcanzado implícitamente cuando termina la cadena en q5
    # Agregamos transición epsilon conceptual a q6
    estados_finales = {'q5'}  # q5 es aceptación
    
    return AFD(estados, alfabeto, transiciones, 'q0', estados_finales)


def crear_afd_base64url():
    """
    AFD que valida si una cadena contiene solo caracteres Base64URL válidos
    A-Z, a-z, 0-9, -, _
    """
    estados = {'q0', 'q1'}
    alfabeto = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_')
    
    transiciones = {}
    for c in alfabeto:
        transiciones[('q0', c)] = 'q1'
        transiciones[('q1', c)] = 'q1'
    
    return AFD(estados, alfabeto, transiciones, 'q0', {'q1'})


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("AFD para validación de estructura JWT")
    print("=" * 60)
    
    afd_jwt = crear_afd_jwt_estructura()
    print(afd_jwt)
    
    # Casos de prueba
    casos_prueba = [
        "eyJhbGc.eyJzdWI.SflKxw",  # Válido
        "header.payload.signature",  # Válido
        "abc.def",  # Inválido (solo 2 partes)
        "abc..def",  # Inválido (payload vacío)
        ".payload.signature",  # Inválido (header vacío)
        "header.payload.signature.extra",  # Inválido (4 partes)
    ]
    
    print("\nPruebas de validación:\n")
    for i, caso in enumerate(casos_prueba, 1):
        aceptado, mensaje = afd_jwt.procesar(caso)
        print(f"{i}. '{caso}'")
        print(f"   {'✓ ACEPTADO' if aceptado else '✗ RECHAZADO'}: {mensaje}\n")
    
    # AFD para Base64URL
    print("\n" + "=" * 60)
    print("AFD para validación de caracteres Base64URL")
    print("=" * 60)
    
    afd_b64 = crear_afd_base64url()
    
    casos_b64 = [
        "eyJhbGciOiJIUzI1NiJ9",  # Válido
        "abc123-_",  # Válido
        "invalid@chars",  # Inválido (@ no es Base64URL)
        "test+test",  # Inválido (+ no es Base64URL, es Base64 estándar)
    ]
    
    print("\nPruebas Base64URL:\n")
    for i, caso in enumerate(casos_b64, 1):
        aceptado, mensaje = afd_b64.procesar(caso)
        print(f"{i}. '{caso}'")
        print(f"   {'✓ ACEPTADO' if aceptado else '✗ RECHAZADO'}: {mensaje}\n")
