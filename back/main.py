"""
Programa principal integrando las Fases 3, 4 y 5
Analizador y Validador completo de JWT
"""

import sys
import os
from datetime import datetime

# Agregar paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analisis_semantico.validador_semantico import ValidadorSemanticoJWT
from decodificacion.decodificador_jwt import ParserJWT
from codificacion.generador_jwt import GeneradorJWT


class AnalizadorValidadorJWT:
    """
    Clase principal que integra todas las fases del proyecto
    """
    
    def __init__(self):
        self.validador_semantico = ValidadorSemanticoJWT()
        self.parser = ParserJWT()
    
    def analizar_completo(self, token_jwt, clave_secreta=None):
        """
        Análisis completo de un JWT:
        1. Parsing (Fase 4)
        2. Validación semántica (Fase 3)
        3. Verificación de firma (Fase 5)
        """
        print("\n" + "="*80)
        print(" "*20 + "ANÁLISIS COMPLETO DE JWT")
        print("="*80)
        
        try:
            # FASE 4: Decodificación
            print("\n[FASE 4] DECODIFICACIÓN")
            componentes = self.parser.parsear(token_jwt)
            claims = self.parser.extraer_claims(componentes['payload'])
            
            # FASE 3: Validación Semántica
            print("\n\n[FASE 3] ANÁLISIS SEMÁNTICO")
            
            header_valido = self.validador_semantico.validar_header(componentes['header'])
            payload_valido = self.validador_semantico.validar_payload(componentes['payload'])
            tabla_valida = self.validador_semantico.validar_tabla_simbolos(componentes['payload'])
            
            semantica_valida = self.validador_semantico.generar_reporte()
            
            # FASE 5: Verificación de firma
            if clave_secreta:
                print("\n\n[FASE 5] VERIFICACIÓN DE FIRMA")
                algoritmo = componentes['header'].get('alg', 'HS256')
                
                if algoritmo in GeneradorJWT.ALGORITMOS_HMAC:
                    generador = GeneradorJWT(algoritmo=algoritmo)
                    firma_valida = generador.verificar_firma(token_jwt, clave_secreta)
                else:
                    print(f"⚠ Algoritmo {algoritmo} no soportado para verificación")
                    firma_valida = None
            else:
                print("\n\n[FASE 5] VERIFICACIÓN DE FIRMA: Omitida (sin clave secreta)")
                firma_valida = None
            
            # Resumen final
            print("\n" + "="*80)
            print(" "*30 + "RESUMEN FINAL")
            print("="*80)
            
            print(f"\n✓ Estructura JWT: VÁLIDA (3 partes)")
            print(f"{'✓' if semantica_valida else '✗'} Validación semántica: {'APROBADA' if semantica_valida else 'FALLÓ'}")
            
            if firma_valida is not None:
                print(f"{'✓' if firma_valida else '✗'} Verificación de firma: {'VÁLIDA' if firma_valida else 'INVÁLIDA'}")
            
            # Mostrar información del token
            print(f"\nInformación del token:")
            print(f"  Algoritmo: {componentes['header'].get('alg')}")
            print(f"  Tipo: {componentes['header'].get('typ')}")
            
            if 'iss' in componentes['payload']:
                print(f"  Emisor: {componentes['payload']['iss']}")
            
            if 'sub' in componentes['payload']:
                print(f"  Sujeto: {componentes['payload']['sub']}")
            
            if 'exp' in componentes['payload']:
                exp = componentes['payload']['exp']
                exp_date = datetime.fromtimestamp(exp)
                print(f"  Expiración: {exp_date}")
            
            print(f"  Claims estándar: {len(claims['estandar'])}")
            print(f"  Claims personalizados: {len(claims['custom'])}")
            
            return {
                'valido': semantica_valida and (firma_valida if firma_valida is not None else True),
                'componentes': componentes,
                'claims': claims,
                'semantica_valida': semantica_valida,
                'firma_valida': firma_valida
            }
            
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None


def menu_principal():
    """
    Menú interactivo para probar el analizador
    """
    print("\n" + "="*80)
    print(" "*15 + "ANALIZADOR Y VALIDADOR DE JWT")
    print(" "*15 + "Proyecto Final - Lenguajes Formales 2025-2")
    print("="*80)
    
    analizador = AnalizadorValidadorJWT()
    
    print("\nOpciones:")
    print("1. Generar nuevo JWT")
    print("2. Analizar JWT existente")
    print("3. Ejecutar casos de prueba")
    print("4. Demostración de autómatas")
    print("5. Salir")
    
    opcion = input("\nSeleccione una opción (1-5): ")
    
    if opcion == '1':
        # Generar nuevo JWT
        print("\n--- GENERACIÓN DE JWT ---")
        
        issuer = input("Issuer (emisor): ")
        subject = input("Subject (sujeto): ")
        minutos = int(input("Expiración (minutos): "))
        clave = input("Clave secreta: ")
        
        generador = GeneradorJWT()
        payload = generador.crear_payload(
            issuer=issuer,
            subject=subject,
            expiracion_minutos=minutos
        )
        
        token = generador.generar_token(payload, clave)
        
        print("\nJWT generado:")
        print(token)
        
        # Analizar el token generado
        input("\nPresione Enter para analizar el token generado...")
        analizador.analizar_completo(token, clave)
    
    elif opcion == '2':
        # Analizar JWT existente
        print("\n--- ANÁLISIS DE JWT ---")
        
        token = input("\nIngrese el JWT a analizar: ")
        usar_clave = input("¿Verificar firma? (s/n): ").lower() == 's'
        
        clave = None
        if usar_clave:
            clave = input("Clave secreta: ")
        
        analizador.analizar_completo(token, clave)
    
    elif opcion == '3':
        # Casos de prueba
        ejecutar_casos_prueba()
    
    elif opcion == '4':
        # Demostración de autómatas
        demostrar_automatas()
    
    elif opcion == '5':
        print("\n¡Hasta luego!")
        return
    
    # Volver al menú
    input("\n\nPresione Enter para volver al menú...")
    menu_principal()


def ejecutar_casos_prueba():
    """
    Ejecuta suite completa de casos de prueba
    """
    print("\n" + "="*80)
    print(" "*25 + "CASOS DE PRUEBA")
    print("="*80)
    
    analizador = AnalizadorValidadorJWT()
    generador = GeneradorJWT()
    clave_secreta = "clave_prueba_2025"
    
    casos = [
        {
            'nombre': 'JWT Válido',
            'payload': {
                'iss': 'auth.example.com',
                'sub': 'user123',
                'exp': int(datetime.now().timestamp()) + 3600,
                'iat': int(datetime.now().timestamp()),
                'rol': 'admin'
            }
        },
        {
            'nombre': 'JWT Expirado',
            'payload': {
                'iss': 'auth.example.com',
                'sub': 'user456',
                'exp': int(datetime.now().timestamp()) - 1000,
                'iat': int(datetime.now().timestamp()) - 5000,
            }
        },
        {
            'nombre': 'JWT con Claims Inválidos',
            'payload': {
                'iss': 12345,  # Debe ser string
                'exp': 'invalid',  # Debe ser int
            }
        }
    ]
    
    for i, caso in enumerate(casos, 1):
        print(f"\n{'='*80}")
        print(f"CASO {i}: {caso['nombre']}")
        print('='*80)
        
        try:
            token = generador.generar_token(caso['payload'], clave_secreta)
            analizador.analizar_completo(token, clave_secreta)
        except Exception as e:
            print(f"Error generando token: {e}")


def demostrar_automatas():
    """
    Demuestra los autómatas implementados
    """
    print("\n" + "="*80)
    print(" "*20 + "DEMOSTRACIÓN DE AUTÓMATAS")
    print("="*80)
    
    print("\n1. AFD - Validación de estructura JWT")
    print("2. AFN - Validación de patrones")
    print("3. AFD Mínimo - Minimización")
    print("4. Construcción de Thompson - ER a AFN")
    
    opcion = input("\nSeleccione (1-4): ")
    
    if opcion == '1':
        from automatas.afd_base import crear_afd_jwt_estructura
        os.system('python automatas/afd_base.py')
    
    elif opcion == '2':
        os.system('python automatas/afn_base.py')
    
    elif opcion == '3':
        os.system('python automatas/minimizador.py')
    
    elif opcion == '4':
        os.system('python automatas/clausula.py')


# Programa principal
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analizador y Validador de JWT')
    parser.add_argument('--token', help='JWT a analizar')
    parser.add_argument('--clave', help='Clave secreta para verificar firma')
    parser.add_argument('--menu', action='store_true', help='Mostrar menú interactivo')
    parser.add_argument('--demo', action='store_true', help='Ejecutar casos de prueba')
    
    args = parser.parse_args()
    
    if args.demo:
        ejecutar_casos_prueba()
    elif args.token:
        analizador = AnalizadorValidadorJWT()
        analizador.analizar_completo(args.token, args.clave)
    else:
        # Menú interactivo por defecto
        menu_principal()
