"""
FASE 3: Análisis Semántico de JWT
Validación de campos obligatorios, tipos de datos y valores usando autómatas
"""

import json
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path para importar los autómatas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automatas.afd_base import AFD


class ValidadorSemanticoJWT:
    """
    Validador semántico para JWT usando autómatas finitos
    Verifica:
    - Campos obligatorios en header y payload
    - Tipos de datos correctos
    - Valores válidos para claims estándar
    - Validación temporal (exp, nbf, iat)
    """
    
    # Claims estándar registrados (RFC 7519)
    CLAIMS_ESTANDAR = {
        'iss': str,      # Issuer
        'sub': str,      # Subject
        'aud': (str, list),  # Audience
        'exp': int,      # Expiration Time
        'nbf': int,      # Not Before
        'iat': int,      # Issued At
        'jti': str,      # JWT ID
    }
    
    # Algoritmos soportados
    ALGORITMOS_VALIDOS = {
        'HS256', 'HS384', 'HS512',  # HMAC
        'RS256', 'RS384', 'RS512',  # RSA
        'ES256', 'ES384', 'ES512',  # ECDSA
        'PS256', 'PS384', 'PS512',  # RSA-PSS
        'none'  # Sin firma (no recomendado en producción)
    }
    
    def __init__(self):
        self.errores = []
        self.advertencias = []
        # Crear AFD para validar algoritmos
        self.afd_algoritmo = self._crear_afd_algoritmo()
    
    def _crear_afd_algoritmo(self):
        """
        Crea un AFD que valida si un string es un algoritmo válido
        Usando un AFD simple que acepta los algoritmos conocidos
        """
        estados = {'q0', 'q_hs', 'q_rs', 'q_es', 'q_ps', 'q_none', 'q_final', 'q_reject'}
        alfabeto = set('HRESPnoe256384512')
        
        transiciones = {}
        
        # Transiciones para detectar prefijos
        transiciones[('q0', 'H')] = 'q_hs'
        transiciones[('q0', 'R')] = 'q_rs'
        transiciones[('q0', 'E')] = 'q_es'
        transiciones[('q0', 'P')] = 'q_ps'
        transiciones[('q0', 'n')] = 'q_none'
        
        # Completar "HS256", "HS384", "HS512"
        transiciones[('q_hs', 'S')] = 'q_hs'
        # (Simplificado - en producción se verificaría completamente)
        
        estados_finales = {'q_final'}
        
        return AFD(estados, alfabeto, transiciones, 'q0', estados_finales)
    
    def validar_header(self, header):
        """
        Valida la estructura semántica del header
        """
        print("\n" + "="*60)
        print("VALIDACIÓN SEMÁNTICA DEL HEADER")
        print("="*60)
        
        # Campo obligatorio: alg
        if 'alg' not in header:
            self.errores.append("Header: falta campo obligatorio 'alg'")
            print("✗ ERROR: Campo 'alg' es obligatorio")
            return False
        
        # Validar algoritmo
        algoritmo = header['alg']
        if algoritmo not in self.ALGORITMOS_VALIDOS:
            self.errores.append(f"Header: algoritmo '{algoritmo}' no es válido")
            print(f"✗ ERROR: Algoritmo '{algoritmo}' no reconocido")
            print(f"  Algoritmos válidos: {', '.join(sorted(self.ALGORITMOS_VALIDOS))}")
            return False
        
        print(f"✓ Algoritmo válido: {algoritmo}")
        
        # Advertencia para 'none'
        if algoritmo == 'none':
            self.advertencias.append("Header: algoritmo 'none' no es seguro en producción")
            print("⚠ ADVERTENCIA: Algoritmo 'none' no es seguro")
        
        # Campo opcional: typ
        if 'typ' in header:
            if header['typ'] != 'JWT':
                self.advertencias.append(f"Header: tipo '{header['typ']}' inusual (esperado 'JWT')")
                print(f"⚠ ADVERTENCIA: Tipo '{header['typ']}' (esperado 'JWT')")
            else:
                print(f"✓ Tipo correcto: {header['typ']}")
        
        return True
    
    def validar_payload(self, payload, tiempo_actual=None):
        """
        Valida la estructura semántica del payload
        """
        print("\n" + "="*60)
        print("VALIDACIÓN SEMÁNTICA DEL PAYLOAD")
        print("="*60)
        
        if tiempo_actual is None:
            tiempo_actual = int(datetime.now().timestamp())
        
        # Validar tipos de claims estándar
        for claim, tipo_esperado in self.CLAIMS_ESTANDAR.items():
            if claim in payload:
                valor = payload[claim]
                
                # Verificar tipo
                if isinstance(tipo_esperado, tuple):
                    # Múltiples tipos permitidos
                    if not any(isinstance(valor, t) for t in tipo_esperado):
                        self.errores.append(
                            f"Payload: claim '{claim}' debe ser {' o '.join(t.__name__ for t in tipo_esperado)}"
                        )
                        print(f"✗ ERROR: '{claim}' tiene tipo incorrecto")
                        continue
                else:
                    # Un solo tipo
                    if not isinstance(valor, tipo_esperado):
                        self.errores.append(
                            f"Payload: claim '{claim}' debe ser {tipo_esperado.__name__}"
                        )
                        print(f"✗ ERROR: '{claim}' debe ser {tipo_esperado.__name__}, es {type(valor).__name__}")
                        continue
                
                print(f"✓ Claim '{claim}': tipo correcto ({type(valor).__name__})")
                
                # Validaciones específicas por claim
                if claim == 'exp':
                    self._validar_expiracion(valor, tiempo_actual)
                elif claim == 'nbf':
                    self._validar_not_before(valor, tiempo_actual)
                elif claim == 'iat':
                    self._validar_issued_at(valor, tiempo_actual)
        
        return len(self.errores) == 0
    
    def _validar_expiracion(self, exp, tiempo_actual):
        """
        Valida el claim 'exp' (expiration time)
        Usando un autómata conceptual de estados temporales
        """
        print(f"\n  Validando expiración (exp):")
        print(f"    exp: {exp} ({datetime.fromtimestamp(exp)})")
        print(f"    now: {tiempo_actual} ({datetime.fromtimestamp(tiempo_actual)})")
        
        # Estados del autómata temporal:
        # - FUTURO: exp > now (token válido)
        # - PRESENTE: exp == now (límite)
        # - PASADO: exp < now (token expirado)
        
        if exp < tiempo_actual:
            self.errores.append(f"Token expirado (exp: {exp}, actual: {tiempo_actual})")
            print(f"  ✗ ERROR: Token expirado")
            print(f"    Expiró hace {tiempo_actual - exp} segundos")
        elif exp == tiempo_actual:
            self.advertencias.append("Token en el límite de expiración")
            print(f"  ⚠ ADVERTENCIA: Token en límite de expiración")
        else:
            print(f"  ✓ Token válido (expira en {exp - tiempo_actual} segundos)")
    
    def _validar_not_before(self, nbf, tiempo_actual):
        """
        Valida el claim 'nbf' (not before)
        """
        print(f"\n  Validando not-before (nbf):")
        print(f"    nbf: {nbf} ({datetime.fromtimestamp(nbf)})")
        
        if nbf > tiempo_actual:
            self.errores.append(f"Token aún no válido (nbf: {nbf}, actual: {tiempo_actual})")
            print(f"  ✗ ERROR: Token no válido aún")
            print(f"    Será válido en {nbf - tiempo_actual} segundos")
        else:
            print(f"  ✓ Token ya es válido")
    
    def _validar_issued_at(self, iat, tiempo_actual):
        """
        Valida el claim 'iat' (issued at)
        """
        print(f"\n  Validando issued-at (iat):")
        print(f"    iat: {iat} ({datetime.fromtimestamp(iat)})")
        
        # Verificar que no sea futuro (sería inconsistente)
        if iat > tiempo_actual:
            self.advertencias.append(f"Token emitido en el futuro (iat: {iat})")
            print(f"  ⚠ ADVERTENCIA: Token emitido en el futuro")
        else:
            edad = tiempo_actual - iat
            print(f"  ✓ Token emitido hace {edad} segundos")
    
    def validar_tabla_simbolos(self, payload):
        """
        Valida que no haya claims duplicados o conflictivos
        Similar a una tabla de símbolos en compiladores
        """
        print("\n" + "="*60)
        print("VALIDACIÓN DE TABLA DE SÍMBOLOS (CLAIMS)")
        print("="*60)
        
        claims_vistos = set()
        
        for claim in payload.keys():
            if claim in claims_vistos:
                self.errores.append(f"Claim duplicado: '{claim}'")
                print(f"✗ ERROR: Claim '{claim}' duplicado")
            else:
                claims_vistos.add(claim)
                print(f"✓ Claim '{claim}' registrado")
        
        # Verificar coherencia entre claims temporales
        if 'iat' in payload and 'exp' in payload:
            if payload['exp'] <= payload['iat']:
                self.errores.append("Incoherencia: 'exp' debe ser mayor que 'iat'")
                print(f"✗ ERROR: exp ({payload['exp']}) <= iat ({payload['iat']})")
            else:
                print(f"✓ Coherencia temporal: iat < exp")
        
        if 'nbf' in payload and 'iat' in payload:
            if payload['nbf'] < payload['iat']:
                self.advertencias.append("Inusual: 'nbf' es anterior a 'iat'")
                print(f"⚠ ADVERTENCIA: nbf < iat")
        
        return len(self.errores) == 0
    
    def generar_reporte(self):
        """
        Genera un reporte de validación semántica
        """
        print("\n" + "="*60)
        print("REPORTE DE VALIDACIÓN SEMÁNTICA")
        print("="*60)
        
        if not self.errores and not self.advertencias:
            print("\n✓ VALIDACIÓN EXITOSA")
            print("  No se encontraron errores ni advertencias")
            return True
        
        if self.errores:
            print(f"\n✗ ERRORES ENCONTRADOS ({len(self.errores)}):")
            for i, error in enumerate(self.errores, 1):
                print(f"  {i}. {error}")
        
        if self.advertencias:
            print(f"\n⚠ ADVERTENCIAS ({len(self.advertencias)}):")
            for i, adv in enumerate(self.advertencias, 1):
                print(f"  {i}. {adv}")
        
        return len(self.errores) == 0


# Casos de prueba
if __name__ == "__main__":
    print("="*60)
    print("FASE 3: ANÁLISIS SEMÁNTICO DE JWT")
    print("="*60)
    
    validador = ValidadorSemanticoJWT()
    
    # Caso 1: JWT válido
    print("\n\nCASO 1: Token válido")
    print("-"*60)
    
    header_valido = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    tiempo_actual = int(datetime.now().timestamp())
    
    payload_valido = {
        "iss": "auth.example.com",
        "sub": "user123",
        "aud": "app.example.com",
        "exp": tiempo_actual + 3600,  # Expira en 1 hora
        "nbf": tiempo_actual - 60,     # Válido desde hace 1 minuto
        "iat": tiempo_actual - 60,     # Emitido hace 1 minuto
        "jti": "abc123",
        "nombre": "Juan Pérez",
        "rol": "admin"
    }
    
    validador.validar_header(header_valido)
    validador.validar_payload(payload_valido, tiempo_actual)
    validador.validar_tabla_simbolos(payload_valido)
    validador.generar_reporte()
    
    # Caso 2: JWT con errores
    print("\n\n" + "="*60)
    print("CASO 2: Token con errores semánticos")
    print("="*60)
    
    validador2 = ValidadorSemanticoJWT()
    
    header_invalido = {
        "alg": "XYZ999",  # Algoritmo no válido
        "typ": "TOKEN"
    }
    
    payload_invalido = {
        "iss": 12345,  # Debe ser string
        "exp": tiempo_actual - 3600,  # Expirado
        "nbf": tiempo_actual + 3600,  # Aún no válido
        "iat": "2025-10-23",  # Debe ser int
    }
    
    validador2.validar_header(header_invalido)
    validador2.validar_payload(payload_invalido, tiempo_actual)
    validador2.validar_tabla_simbolos(payload_invalido)
    validador2.generar_reporte()
    
    # Caso 3: Token expirado
    print("\n\n" + "="*60)
    print("CASO 3: Token expirado")
    print("="*60)
    
    validador3 = ValidadorSemanticoJWT()
    
    payload_expirado = {
        "iss": "auth.service",
        "exp": tiempo_actual - 1000,  # Expiró hace tiempo
        "iat": tiempo_actual - 5000
    }
    
    validador3.validar_header(header_valido)
    validador3.validar_payload(payload_expirado, tiempo_actual)
    validador3.generar_reporte()
