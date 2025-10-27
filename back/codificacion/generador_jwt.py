"""
FASE 5: Codificación y Firma de JWT
Generación de JWT desde objetos JSON
"""

import json
import hmac
import hashlib
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decodificacion.decodificador_jwt import DecodificadorBase64URL


class GeneradorJWT:
    """
    Genera JWT completos desde objetos Python
    Implementa firma usando HMAC (HS256, HS384, HS512)
    """
    
    ALGORITMOS_HMAC = {
        'HS256': hashlib.sha256,
        'HS384': hashlib.sha384,
        'HS512': hashlib.sha512,
    }
    
    def __init__(self, algoritmo='HS256'):
        if algoritmo not in self.ALGORITMOS_HMAC:
            raise ValueError(f"Algoritmo {algoritmo} no soportado. Use: {list(self.ALGORITMOS_HMAC.keys())}")
        
        self.algoritmo = algoritmo
        self.codificador = DecodificadorBase64URL()
    
    def crear_header(self, tipo='JWT'):
        """
        Crea el header del JWT
        """
        return {
            'alg': self.algoritmo,
            'typ': tipo
        }
    
    def crear_payload(self, issuer=None, subject=None, audience=None, 
                     expiracion_minutos=60, claims_custom=None):
        """
        Crea el payload con claims estándar y personalizados
        """
        print(f"\n{'='*60}")
        print("GENERACIÓN DE PAYLOAD")
        print(f"{'='*60}")
        
        ahora = datetime.now()
        payload = {}
        
        # Claims estándar
        if issuer:
            payload['iss'] = issuer
            print(f"  iss (Issuer): {issuer}")
        
        if subject:
            payload['sub'] = subject
            print(f"  sub (Subject): {subject}")
        
        if audience:
            payload['aud'] = audience
            print(f"  aud (Audience): {audience}")
        
        # Timestamps
        payload['iat'] = int(ahora.timestamp())
        print(f"  iat (Issued At): {payload['iat']} ({ahora})")
        
        if expiracion_minutos:
            exp_time = ahora + timedelta(minutes=expiracion_minutos)
            payload['exp'] = int(exp_time.timestamp())
            print(f"  exp (Expiration): {payload['exp']} ({exp_time})")
            print(f"      Válido por {expiracion_minutos} minutos")
        
        # Claims personalizados
        if claims_custom:
            print(f"\n  Claims personalizados:")
            for key, value in claims_custom.items():
                payload[key] = value
                print(f"    {key}: {value}")
        
        return payload
    
    def firmar(self, mensaje, clave_secreta):
        """
        Firma el mensaje usando HMAC
        
        HMAC (Hash-based Message Authentication Code):
        - Combina función hash con clave secreta
        - Garantiza integridad y autenticidad
        - Proceso: HMAC(K, M) = H((K ⊕ opad) || H((K ⊕ ipad) || M))
        """
        print(f"\n{'='*60}")
        print("PROCESO DE FIRMA (HMAC)")
        print(f"{'='*60}")
        
        print(f"\nAlgoritmo: {self.algoritmo}")
        print(f"Hash subyacente: {self.ALGORITMOS_HMAC[self.algoritmo].__name__}")
        
        if isinstance(mensaje, str):
            mensaje = mensaje.encode('utf-8')
        
        if isinstance(clave_secreta, str):
            clave_secreta = clave_secreta.encode('utf-8')
        
        print(f"\nPaso 1 - Datos de entrada:")
        print(f"  Mensaje: {len(mensaje)} bytes")
        print(f"  Clave secreta: {len(clave_secreta)} bytes")
        
        # Crear HMAC
        print(f"\nPaso 2 - Calcular HMAC:")
        hash_func = self.ALGORITMOS_HMAC[self.algoritmo]
        firma = hmac.new(clave_secreta, mensaje, hash_func).digest()
        
        print(f"  Firma generada: {len(firma)} bytes")
        print(f"  Hex: {firma.hex()}")
        
        return firma
    
    def generar_token(self, payload, clave_secreta, header=None):
        """
        Genera un JWT completo firmado
        """
        print(f"\n{'='*60}")
        print("GENERACIÓN DE JWT COMPLETO")
        print(f"{'='*60}")
        
        # Paso 1: Crear header
        if header is None:
            header = self.crear_header()
        
        print(f"\nPaso 1 - Header:")
        print(f"  {json.dumps(header, indent=2)}")
        
        # Paso 2: Codificar header
        header_json = json.dumps(header, separators=(',', ':'))
        header_b64 = self.codificador.codificar(header_json)
        print(f"\nPaso 2 - Header codificado (Base64URL):")
        print(f"  {header_b64}")
        
        # Paso 3: Codificar payload
        print(f"\nPaso 3 - Payload:")
        print(f"  {json.dumps(payload, indent=2)}")
        
        payload_json = json.dumps(payload, separators=(',', ':'))
        payload_b64 = self.codificador.codificar(payload_json)
        print(f"\n  Payload codificado (Base64URL):")
        print(f"  {payload_b64}")
        
        # Paso 4: Crear mensaje a firmar
        mensaje = f"{header_b64}.{payload_b64}"
        print(f"\nPaso 4 - Mensaje a firmar:")
        print(f"  {mensaje[:80]}{'...' if len(mensaje) > 80 else ''}")
        
        # Paso 5: Firmar
        firma_bytes = self.firmar(mensaje, clave_secreta)
        firma_b64 = self.codificador.codificar(firma_bytes)
        
        print(f"\nPaso 5 - Firma (Base64URL):")
        print(f"  {firma_b64}")
        
        # Paso 6: Ensamblar JWT
        token = f"{mensaje}.{firma_b64}"
        
        print(f"\n{'='*60}")
        print("JWT GENERADO")
        print(f"{'='*60}")
        print(f"\n{token}\n")
        print(f"Longitud total: {len(token)} caracteres")
        
        return token
    
    def verificar_firma(self, token, clave_secreta):
        """
        Verifica la firma de un JWT
        """
        print(f"\n{'='*60}")
        print("VERIFICACIÓN DE FIRMA")
        print(f"{'='*60}")
        
        # Separar componentes
        partes = token.split('.')
        if len(partes) != 3:
            print("✗ Token inválido: debe tener 3 partes")
            return False
        
        header_b64, payload_b64, firma_b64 = partes
        
        # Recrear mensaje
        mensaje = f"{header_b64}.{payload_b64}"
        print(f"\nMensaje firmado: {mensaje[:80]}{'...' if len(mensaje) > 80 else ''}")
        
        # Calcular firma esperada
        firma_esperada = self.firmar(mensaje, clave_secreta)
        firma_esperada_b64 = self.codificador.codificar(firma_esperada)
        
        print(f"\nFirma en token:   {firma_b64}")
        print(f"Firma calculada:  {firma_esperada_b64}")
        
        # Comparar (timing-safe)
        if hmac.compare_digest(firma_b64, firma_esperada_b64):
            print(f"\n✓ FIRMA VÁLIDA")
            return True
        else:
            print(f"\n✗ FIRMA INVÁLIDA")
            return False


# Casos de prueba
if __name__ == "__main__":
    print("="*60)
    print("FASE 5: CODIFICACIÓN Y FIRMA DE JWT")
    print("="*60)
    
    # Caso 1: Generar JWT simple
    print("\n\nCASO 1: Generar JWT con HS256")
    print("-"*60)
    
    generador = GeneradorJWT(algoritmo='HS256')
    
    payload = generador.crear_payload(
        issuer="auth.universidad.edu",
        subject="estudiante123",
        audience="portal.universidad.edu",
        expiracion_minutos=120,
        claims_custom={
            "nombre": "María García",
            "carrera": "Ingeniería en Sistemas",
            "rol": "estudiante",
            "semestre": 8
        }
    )
    
    clave_secreta = "mi_clave_super_secreta_2025"
    
    token = generador.generar_token(payload, clave_secreta)
    
    # Verificar el token generado
    print("\n" + "="*60)
    print("VERIFICACIÓN DEL TOKEN GENERADO")
    print("="*60)
    
    es_valido = generador.verificar_firma(token, clave_secreta)
    
    # Caso 2: Verificar con clave incorrecta
    print("\n\nCASO 2: Verificar con clave incorrecta")
    print("-"*60)
    
    clave_incorrecta = "clave_incorrecta"
    es_valido_incorrecto = generador.verificar_firma(token, clave_incorrecta)
    
    # Caso 3: Diferentes algoritmos
    print("\n\nCASO 3: Generar con diferentes algoritmos")
    print("-"*60)
    
    for algoritmo in ['HS256', 'HS384', 'HS512']:
        print(f"\n--- {algoritmo} ---")
        gen = GeneradorJWT(algoritmo=algoritmo)
        
        payload_simple = {
            "sub": "usuario",
            "iat": int(datetime.now().timestamp())
        }
        
        token_alg = gen.generar_token(payload_simple, clave_secreta)
        print(f"\nLongitud del token: {len(token_alg)} caracteres")
        
        # Verificar
        gen.verificar_firma(token_alg, clave_secreta)
    
    # Caso 4: JWT con claims temporales
    print("\n\nCASO 4: JWT para sesión temporal")
    print("-"*60)
    
    generador_sesion = GeneradorJWT()
    
    payload_sesion = generador_sesion.crear_payload(
        issuer="sistema.autenticacion",
        subject="admin@example.com",
        expiracion_minutos=30,  # Sesión de 30 minutos
        claims_custom={
            "tipo": "sesion",
            "permisos": ["leer", "escribir", "eliminar"],
            "ip": "192.168.1.100"
        }
    )
    
    token_sesion = generador_sesion.generar_token(payload_sesion, clave_secreta)
    
    print("\n✓ JWT de sesión generado exitosamente")
