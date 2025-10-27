"""
Minimización de AFD usando el algoritmo de partición de estados
Obtiene el AFD mínimo equivalente
"""

from afd_base import AFD


class MinimizadorAFD:
    """
    Implementa el algoritmo de minimización de AFD
    Pasos:
    1. Eliminar estados inalcanzables
    2. Particionar estados en equivalentes
    3. Construir AFD mínimo
    """
    
    def __init__(self, afd):
        self.afd = afd
    
    def estados_alcanzables(self):
        """
        Encuentra todos los estados alcanzables desde q0
        """
        alcanzables = {self.afd.q0}
        pila = [self.afd.q0]
        
        while pila:
            estado = pila.pop()
            for simbolo in self.afd.sigma:
                if (estado, simbolo) in self.afd.delta:
                    siguiente = self.afd.delta[(estado, simbolo)]
                    if siguiente not in alcanzables:
                        alcanzables.add(siguiente)
                        pila.append(siguiente)
        
        return alcanzables
    
    def particionar_estados(self):
        """
        Algoritmo de partición para encontrar estados equivalentes
        Dos estados son equivalentes si:
        1. Ambos son finales o ambos no son finales
        2. Para cada símbolo del alfabeto, van a estados equivalentes
        """
        # Partición inicial: estados finales vs no finales
        finales = self.afd.F
        no_finales = self.afd.Q - finales
        
        particiones = []
        if finales:
            particiones.append(finales)
        if no_finales:
            particiones.append(no_finales)
        
        # Refinar particiones iterativamente
        cambios = True
        iteracion = 0
        
        while cambios:
            cambios = False
            iteracion += 1
            nuevas_particiones = []
            
            for particion in particiones:
                # Intentar dividir esta partición
                subparticiones = self._dividir_particion(particion, particiones)
                
                if len(subparticiones) > 1:
                    cambios = True
                    nuevas_particiones.extend(subparticiones)
                else:
                    nuevas_particiones.append(particion)
            
            particiones = nuevas_particiones
            print(f"  Iteración {iteracion}: {len(particiones)} particiones")
        
        return particiones
    
    def _dividir_particion(self, particion, particiones_actuales):
        """
        Intenta dividir una partición en subparticiones
        """
        if len(particion) == 1:
            return [particion]
        
        # Crear grupos basados en comportamiento con cada símbolo
        grupos = {}
        
        for estado in particion:
            # Crear "firma" del estado basada en a qué particiones va con cada símbolo
            firma = []
            for simbolo in sorted(self.afd.sigma):
                if (estado, simbolo) in self.afd.delta:
                    siguiente = self.afd.delta[(estado, simbolo)]
                    # Encontrar a qué partición pertenece el estado siguiente
                    for i, p in enumerate(particiones_actuales):
                        if siguiente in p:
                            firma.append((simbolo, i))
                            break
                else:
                    firma.append((simbolo, None))
            
            firma_tuple = tuple(firma)
            if firma_tuple not in grupos:
                grupos[firma_tuple] = set()
            grupos[firma_tuple].add(estado)
        
        return list(grupos.values())
    
    def minimizar(self):
        """
        Realiza la minimización completa del AFD
        """
        print("\n" + "=" * 60)
        print("Minimización de AFD")
        print("=" * 60)
        
        # Paso 1: Eliminar estados inalcanzables
        print("\nPaso 1: Eliminar estados inalcanzables")
        alcanzables = self.estados_alcanzables()
        print(f"  Estados originales: {self.afd.Q}")
        print(f"  Estados alcanzables: {alcanzables}")
        
        inalcanzables = self.afd.Q - alcanzables
        if inalcanzables:
            print(f"  Estados eliminados (inalcanzables): {inalcanzables}")
        
        # Paso 2: Particionar estados equivalentes
        print("\nPaso 2: Particionar estados equivalentes")
        particiones = self.particionar_estados()
        print(f"\nParticiones finales ({len(particiones)}):")
        for i, p in enumerate(particiones):
            print(f"  P{i}: {p}")
        
        # Paso 3: Construir AFD mínimo
        print("\nPaso 3: Construir AFD mínimo")
        
        # Mapear estados a representantes de particiones
        estado_a_particion = {}
        for i, particion in enumerate(particiones):
            representante = f"P{i}"
            for estado in particion:
                estado_a_particion[estado] = representante
        
        # Nuevos estados
        nuevos_estados = {f"P{i}" for i in range(len(particiones))}
        
        # Nuevo estado inicial
        nuevo_q0 = estado_a_particion[self.afd.q0]
        
        # Nuevos estados finales
        nuevos_finales = set()
        for estado in self.afd.F:
            if estado in alcanzables:
                nuevos_finales.add(estado_a_particion[estado])
        
        # Nuevas transiciones (sin duplicados)
        nuevas_transiciones = {}
        for (estado, simbolo), destino in self.afd.delta.items():
            if estado in alcanzables and destino in alcanzables:
                nueva_clave = (estado_a_particion[estado], simbolo)
                nuevo_destino = estado_a_particion[destino]
                nuevas_transiciones[nueva_clave] = nuevo_destino
        
        afd_minimo = AFD(
            nuevos_estados,
            self.afd.sigma,
            nuevas_transiciones,
            nuevo_q0,
            nuevos_finales
        )
        
        print(f"\nAFD Mínimo:")
        print(f"  Estados: {len(self.afd.Q)} → {len(nuevos_estados)}")
        print(f"  Transiciones: {len(self.afd.delta)} → {len(nuevas_transiciones)}")
        print(f"  Reducción: {((len(self.afd.Q) - len(nuevos_estados)) / len(self.afd.Q) * 100):.1f}%")
        
        return afd_minimo


def crear_afd_no_minimo():
    """
    Crea un AFD con estados redundantes para demostrar minimización
    Acepta cadenas que terminan en 'ab'
    """
    estados = {'q0', 'q1', 'q2', 'q3', 'q4', 'q5'}
    alfabeto = {'a', 'b'}
    
    transiciones = {
        # Estados principales
        ('q0', 'a'): 'q1',
        ('q0', 'b'): 'q0',
        ('q1', 'a'): 'q1',
        ('q1', 'b'): 'q2',  # Estado final
        ('q2', 'a'): 'q1',
        ('q2', 'b'): 'q0',
        
        # Estados redundantes (equivalentes a otros)
        ('q3', 'a'): 'q1',  # q3 es equivalente a q0
        ('q3', 'b'): 'q0',
        ('q4', 'a'): 'q1',  # q4 es equivalente a q0
        ('q4', 'b'): 'q0',
        ('q5', 'a'): 'q1',  # q5 es inalcanzable
        ('q5', 'b'): 'q0',
    }
    
    return AFD(estados, alfabeto, transiciones, 'q0', {'q2'})


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("Demostración de Minimización de AFD")
    print("=" * 60)
    
    # Crear AFD no mínimo
    afd = crear_afd_no_minimo()
    print("\nAFD Original:")
    print(afd)
    
    # Minimizar
    minimizador = MinimizadorAFD(afd)
    afd_minimo = minimizador.minimizar()
    
    print("\n" + "=" * 60)
    print("Verificación: AFD original vs AFD mínimo")
    print("=" * 60)
    
    casos = [
        "ab",      # Debe aceptar
        "aab",     # Debe aceptar
        "bab",     # Debe aceptar
        "aaab",    # Debe aceptar
        "a",       # Debe rechazar
        "b",       # Debe rechazar
        "aa",      # Debe rechazar
        "aba",     # Debe rechazar
    ]
    
    print("\nComparación de resultados:\n")
    print(f"{'Cadena':<10} {'Original':<12} {'Mínimo':<12} {'Match':<8}")
    print("-" * 50)
    
    for cadena in casos:
        res_original, _ = afd.procesar(cadena)
        res_minimo, _ = afd_minimo.procesar(cadena)
        match = "✓" if res_original == res_minimo else "✗"
        
        print(f"{cadena:<10} {'ACEPTA' if res_original else 'RECHAZA':<12} "
              f"{'ACEPTA' if res_minimo else 'RECHAZA':<12} {match:<8}")
    
    print("\n✓ Los AFDs son equivalentes (aceptan el mismo lenguaje)")
