"""
Script de demostración interactiva
Ejecuta ejemplos de todas las fases con explicaciones
"""

import sys
import os
from datetime import datetime
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automatas.afd_base import crear_afd_jwt_estructura, crear_afd_base64url
from automatas.afn_base import crear_afn_email_pattern
from automatas.minimizador import MinimizadorAFD, crear_afd_no_minimo
from automatas.clausula import ConstructorThompson
from codificacion.generador_jwt import GeneradorJWT


def pausa():
    """Pausa para lectura"""
    input("\n[Presione Enter para continuar...]")


def titulo(texto):
    """Imprime un título formateado"""
    print("\n" + "="*80)
    print(f"{texto.center(80)}")
    print("="*80)


def demo_afd():
    """Demostración de AFD"""
    titulo("DEMOSTRACIÓN: AUTÓMATA FINITO DETERMINISTA (AFD)")
    
    print("\n📚 TEORÍA:")
    print("   AFD = (Q, Σ, δ, q0, F)")
    print("   - Q: Conjunto finito de estados")
    print("   - Σ: Alfabeto de entrada")
    print("   - δ: Q × Σ → Q (función de transición)")
    print("   - q0: Estado inicial")
    print("   - F ⊆ Q: Estados finales")
    
    print("\n🎯 APLICACIÓN: Validar estructura JWT (header.payload.signature)")
    
    pausa()
    
    afd = crear_afd_jwt_estructura()
    
    print("\n🔧 AFD Creado:")
    print(f"   Estados: {len(afd.Q)}")
    print(f"   Alfabeto: Base64URL + punto")
    print(f"   Transiciones: {len(afd.delta)}")
    
    print("\n📝 Casos de Prueba:")
    casos = [
        ("abc.def.ghi", True, "Estructura válida"),
        ("abc.def", False, "Solo 2 partes (falta signature)"),
        ("a.b.c.d", False, "4 partes (exceso)"),
        (".payload.sig", False, "Header vacío"),
    ]
    
    for i, (caso, esperado, descripcion) in enumerate(casos, 1):
        print(f"\n   {i}. Entrada: '{caso}'")
        print(f"      Descripción: {descripcion}")
        
        aceptado, mensaje = afd.procesar(caso)
        simbolo = "✓" if aceptado == esperado else "✗"
        
        print(f"      Resultado: {simbolo} {'ACEPTA' if aceptado else 'RECHAZA'}")
        print(f"      Mensaje: {mensaje}")
        
        time.sleep(0.5)
    
    pausa()


def demo_afn():
    """Demostración de AFN"""
    titulo("DEMOSTRACIÓN: AUTÓMATA FINITO NO DETERMINISTA (AFN)")
    
    print("\n📚 TEORÍA:")
    print("   AFN permite:")
    print("   - Múltiples transiciones desde un estado con el mismo símbolo")
    print("   - Transiciones ε (sin consumir entrada)")
    print("   - Procesamiento: ε-clausura y conjunto de estados")
    
    print("\n🎯 APLICACIÓN: Validar patrones de email en claims JWT")
    
    pausa()
    
    afn = crear_afn_email_pattern()
    
    print("\n🔧 AFN Creado para pattern: user@domain.tld")
    print(f"   Estados: {len(afn.Q)}")
    print(f"   Incluye ε-transiciones: Sí")
    
    print("\n📝 Casos de Prueba:")
    emails = [
        ("user@example.com", "Email válido"),
        ("admin@site.org", "Email válido"),
        ("invalid.email", "Sin @"),
        ("@nodomain.com", "Sin parte local"),
    ]
    
    for email, descripcion in emails:
        print(f"\n   • {email}")
        print(f"     {descripcion}")
        
        aceptado, mensaje = afn.procesar(email)
        print(f"     Resultado: {'✓ ACEPTA' if aceptado else '✗ RECHAZA'}")
        
        time.sleep(0.5)
    
    pausa()


def demo_minimizacion():
    """Demostración de minimización"""
    titulo("DEMOSTRACIÓN: MINIMIZACIÓN DE AFD")
    
    print("\n📚 TEORÍA:")
    print("   Algoritmo de partición de estados equivalentes:")
    print("   1. Separar estados finales de no finales")
    print("   2. Refinar particiones iterativamente")
    print("   3. Estados en misma partición → equivalentes")
    print("   4. Construir AFD mínimo con representantes")
    
    print("\n🎯 OBJETIVO: Optimizar autómata eliminando redundancias")
    
    pausa()
    
    print("\n🔧 Creando AFD no mínimo...")
    afd = crear_afd_no_minimo()
    
    print(f"\n   AFD Original:")
    print(f"   - Estados: {len(afd.Q)}")
    print(f"   - Transiciones: {len(afd.delta)}")
    print(f"   - Estados: {afd.Q}")
    
    pausa()
    
    print("\n⚙️  Ejecutando minimización...")
    minimizador = MinimizadorAFD(afd)
    afd_minimo = minimizador.minimizar()
    
    print(f"\n✨ AFD Mínimo:")
    print(f"   - Estados: {len(afd_minimo.Q)}")
    print(f"   - Transiciones: {len(afd_minimo.delta)}")
    print(f"   - Reducción: {((len(afd.Q) - len(afd_minimo.Q)) / len(afd.Q) * 100):.1f}%")
    
    print("\n🧪 Verificando equivalencia...")
    casos = ["ab", "aab", "a", "b"]
    
    for caso in casos:
        res_orig, _ = afd.procesar(caso)
        res_min, _ = afd_minimo.procesar(caso)
        match = "✓" if res_orig == res_min else "✗"
        
        print(f"   '{caso}': {match} Equivalente")
    
    pausa()


def demo_thompson():
    """Demostración de Construcción de Thompson"""
    titulo("DEMOSTRACIÓN: CONSTRUCCIÓN DE THOMPSON (ER → AFN)")
    
    print("\n📚 TEORÍA:")
    print("   Algoritmo para convertir expresiones regulares a AFN")
    print("   Operaciones básicas:")
    print("   - Concatenación: r₁·r₂")
    print("   - Unión: r₁|r₂")
    print("   - Clausura de Kleene: r*")
    print("   - Clausura positiva: r+")
    
    print("\n🎯 APLICACIÓN: Validar patrones en claims de JWT")
    
    pausa()
    
    constructor = ConstructorThompson()
    
    # Ejemplo 1: Unión
    print("\n📝 Ejemplo 1: Unión (a|b)")
    print("   ER: a|b")
    print("   Lenguaje: {a, b}")
    
    afn_union = constructor.desde_expresion_simple('a|b')
    print(f"\n   AFN generado:")
    print(f"   - Estados: {len(afn_union.Q)}")
    print(f"   - Transiciones ε: Sí (para unión)")
    
    for cadena in ['a', 'b', 'c']:
        aceptado, _ = afn_union.procesar(cadena)
        print(f"   '{cadena}': {'✓ ACEPTA' if aceptado else '✗ RECHAZA'}")
    
    pausa()
    
    # Ejemplo 2: Clausura de Kleene
    print("\n📝 Ejemplo 2: Clausura de Kleene (a*)")
    print("   ER: a*")
    print("   Lenguaje: {ε, a, aa, aaa, ...}")
    
    afn_kleene = constructor.desde_expresion_simple('a*')
    print(f"\n   AFN generado:")
    print(f"   - Estados: {len(afn_kleene.Q)}")
    print(f"   - Permite cadena vacía: Sí")
    
    for cadena in ['', 'a', 'aa', 'aaa', 'b']:
        aceptado, _ = afn_kleene.procesar(cadena)
        print(f"   '{cadena}': {'✓ ACEPTA' if aceptado else '✗ RECHAZA'}")
    
    pausa()
    
    # Ejemplo 3: Concatenación
    print("\n📝 Ejemplo 3: Concatenación (ab)")
    print("   ER: ab")
    print("   Lenguaje: {ab}")
    
    afn_concat = constructor.desde_expresion_simple('ab')
    
    for cadena in ['ab', 'a', 'b', 'ba']:
        aceptado, _ = afn_concat.procesar(cadena)
        print(f"   '{cadena}': {'✓ ACEPTA' if aceptado else '✗ RECHAZA'}")
    
    pausa()


def demo_jwt_completo():
    """Demostración completa de JWT"""
    titulo("DEMOSTRACIÓN: GENERACIÓN Y VALIDACIÓN COMPLETA DE JWT")
    
    print("\n🎯 FLUJO COMPLETO:")
    print("   1. Generar payload con claims")
    print("   2. Codificar en Base64URL")
    print("   3. Firmar con HMAC")
    print("   4. Validar estructura (AFD)")
    print("   5. Decodificar")
    print("   6. Validar semántica")
    print("   7. Verificar firma")
    
    pausa()
    
    # Paso 1: Generar
    print("\n📝 PASO 1: Generar Payload")
    generador = GeneradorJWT(algoritmo='HS256')
    
    payload = {
        'iss': 'universidad.edu',
        'sub': 'estudiante123',
        'nombre': 'Ana García',
        'carrera': 'Ingeniería en Sistemas',
        'semestre': 8,
        'iat': int(datetime.now().timestamp()),
        'exp': int(datetime.now().timestamp()) + 3600
    }
    
    for key, value in payload.items():
        print(f"   {key}: {value}")
    
    pausa()
    
    # Paso 2: Generar token
    print("\n📝 PASO 2: Generar JWT Firmado")
    clave_secreta = "clave_super_secreta_2025"
    
    token = generador.generar_token(payload, clave_secreta)
    
    print(f"\n   JWT Generado:")
    print(f"   {token[:80]}...")
    print(f"   Longitud: {len(token)} caracteres")
    
    pausa()
    
    # Paso 3: Validar estructura
    print("\n📝 PASO 3: Validar Estructura con AFD")
    afd = crear_afd_jwt_estructura()
    
    partes = token.split('.')
    estructura_simple = f"{'x'*10}.{'y'*10}.{'z'*10}"
    
    aceptado, _ = afd.procesar(estructura_simple)
    print(f"   Estructura: {'✓ VÁLIDA' if aceptado else '✗ INVÁLIDA'}")
    print(f"   Partes: {len(partes)}")
    
    pausa()
    
    # Paso 4: Verificar firma
    print("\n📝 PASO 4: Verificar Firma HMAC-SHA256")
    
    firma_valida = generador.verificar_firma(token, clave_secreta)
    print(f"   Firma: {'✓ VÁLIDA' if firma_valida else '✗ INVÁLIDA'}")
    
    print("\n   Probando con clave incorrecta...")
    firma_invalida = generador.verificar_firma(token, "clave_incorrecta")
    print(f"   Firma: {'✗ INVÁLIDA' if not firma_invalida else '✓ VÁLIDA'} (esperado)")
    
    pausa()


def menu():
    """Menú principal de demostración"""
    while True:
        titulo("PROYECTO FINAL: ANALIZADOR Y VALIDADOR DE JWT")
        print("\n   Aplicación de Lenguajes Formales y Teoría de Autómatas")
        print("   Lenguajes Formales 2025-2")
        
        print("\n📚 Demostraciones Disponibles:")
        print("\n   1. AFD - Autómata Finito Determinista")
        print("   2. AFN - Autómata Finito No Determinista")
        print("   3. Minimización de AFD")
        print("   4. Construcción de Thompson (ER → AFN)")
        print("   5. JWT Completo (Todas las Fases)")
        print("   6. Ejecutar TODAS las demos")
        print("   0. Salir")
        
        opcion = input("\n👉 Seleccione una opción (0-6): ")
        
        if opcion == '1':
            demo_afd()
        elif opcion == '2':
            demo_afn()
        elif opcion == '3':
            demo_minimizacion()
        elif opcion == '4':
            demo_thompson()
        elif opcion == '5':
            demo_jwt_completo()
        elif opcion == '6':
            demo_afd()
            demo_afn()
            demo_minimizacion()
            demo_thompson()
            demo_jwt_completo()
            
            titulo("¡DEMOSTRACIÓN COMPLETA FINALIZADA!")
            print("\n✅ Has visto todas las demostraciones")
            print("📖 Revisa la documentación para más detalles")
            pausa()
        elif opcion == '0':
            titulo("¡HASTA LUEGO!")
            print("\n   Gracias por explorar el proyecto")
            print("   Aplicación exitosa de Lenguajes Formales ✨")
            print("\n")
            break
        else:
            print("\n❌ Opción no válida")
            time.sleep(1)


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
