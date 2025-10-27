"""
FASE 4: Decodificación de JWT
Implementa decodificador Base64URL y parser JSON
"""

import base64
import json


class DecodificadorBase64URL:
    """
    Decodificador Base64URL según RFC 4648
    Base64URL es como Base64 estándar pero:
    - Usa '-' en lugar de '+'
    - Usa '_' en lugar de '/'
    - Sin padding '=' (o padding opcional)
    """
    
    @staticmethod
    def decodificar(cadena_base64url):
        """
        Decodifica una cadena Base64URL a bytes
        """
        print(f"\n{'='*60}")
        print("DECODIFICACIÓN BASE64URL")
        print(f"{'='*60}")
        print(f"Input: {cadena_base64url}")
        print(f"Longitud: {len(cadena_base64url)} caracteres")
        
        # Base64URL → Base64 estándar
        # Paso 1: Reemplazar caracteres
        cadena_base64 = cadena_base64url.replace('-', '+').replace('_', '/')
        print(f"\nPaso 1 - Conversión URL→estándar:")
        print(f"  - → +")
        print(f"  _ → /")
        print(f"  Resultado: {cadena_base64}")
        
        # Paso 2: Agregar padding si es necesario
        # Base64 requiere que la longitud sea múltiplo de 4
        padding_necesario = (4 - len(cadena_base64) % 4) % 4
        
        if padding_necesario > 0:
            cadena_base64 += '=' * padding_necesario
            print(f"\nPaso 2 - Agregar padding:")
            print(f"  Padding necesario: {padding_necesario} caracteres '='")
            print(f"  Resultado: {cadena_base64}")
        else:
            print(f"\nPaso 2 - Sin padding necesario")
        
        # Paso 3: Decodificar Base64
        try:
            bytes_decodificados = base64.b64decode(cadena_base64)
            print(f"\nPaso 3 - Decodificación Base64:")
            print(f"  Bytes resultantes: {len(bytes_decodificados)} bytes")
            print(f"  ✓ Decodificación exitosa")
            return bytes_decodificados
        
        except Exception as e:
            print(f"\n✗ ERROR en decodificación: {e}")
            raise ValueError(f"Error decodificando Base64URL: {e}")
    
    @staticmethod
    def codificar(datos):
        """
        Codifica bytes a Base64URL
        """
        print(f"\n{'='*60}")
        print("CODIFICACIÓN BASE64URL")
        print(f"{'='*60}")
        
        if isinstance(datos, str):
            datos = datos.encode('utf-8')
        
        print(f"Input: {len(datos)} bytes")
        
        # Paso 1: Codificar en Base64 estándar
        base64_estandar = base64.b64encode(datos).decode('ascii')
        print(f"\nPaso 1 - Codificación Base64 estándar:")
        print(f"  {base64_estandar}")
        
        # Paso 2: Convertir a Base64URL
        base64url = base64_estandar.replace('+', '-').replace('/', '_')
        print(f"\nPaso 2 - Conversión estándar→URL:")
        print(f"  + → -")
        print(f"  / → _")
        print(f"  {base64url}")
        
        # Paso 3: Remover padding
        base64url = base64url.rstrip('=')
        print(f"\nPaso 3 - Remover padding:")
        print(f"  {base64url}")
        print(f"  Longitud final: {len(base64url)} caracteres")
        print(f"  ✓ Codificación exitosa")
        
        return base64url


class ParserJWT:
    """
    Parser para JWT completo
    Separa header, payload y signature
    """
    
    def __init__(self):
        self.decodificador = DecodificadorBase64URL()
    
    def parsear(self, token_jwt):
        """
        Parsea un JWT completo y retorna sus componentes
        """
        print(f"\n{'='*60}")
        print("PARSING DE JWT")
        print(f"{'='*60}")
        
        # Paso 1: Validar estructura (debe tener 3 partes)
        partes = token_jwt.split('.')
        
        print(f"\nPaso 1 - Validación de estructura:")
        print(f"  Token: {token_jwt[:50]}{'...' if len(token_jwt) > 50 else ''}")
        print(f"  Partes encontradas: {len(partes)}")
        
        if len(partes) != 3:
            raise ValueError(f"JWT inválido: debe tener 3 partes, encontradas {len(partes)}")
        
        print(f"  ✓ Estructura válida (3 partes)")
        
        header_b64, payload_b64, signature_b64 = partes
        
        print(f"\n  Header (Base64URL): {header_b64}")
        print(f"  Payload (Base64URL): {payload_b64[:50]}{'...' if len(payload_b64) > 50 else ''}")
        print(f"  Signature (Base64URL): {signature_b64[:50]}{'...' if len(signature_b64) > 50 else ''}")
        
        # Paso 2: Decodificar header
        print(f"\n{'='*60}")
        print("Decodificando HEADER")
        print(f"{'='*60}")
        
        header_bytes = self.decodificador.decodificar(header_b64)
        header_json = header_bytes.decode('utf-8')
        header = json.loads(header_json)
        
        print(f"\nJSON decodificado:")
        print(f"  {json.dumps(header, indent=2)}")
        
        # Paso 3: Decodificar payload
        print(f"\n{'='*60}")
        print("Decodificando PAYLOAD")
        print(f"{'='*60}")
        
        payload_bytes = self.decodificador.decodificar(payload_b64)
        payload_json = payload_bytes.decode('utf-8')
        payload = json.loads(payload_json)
        
        print(f"\nJSON decodificado:")
        print(f"  {json.dumps(payload, indent=2)}")
        
        # Paso 4: Signature (mantener en Base64URL)
        print(f"\n{'='*60}")
        print("SIGNATURE")
        print(f"{'='*60}")
        print(f"  Signature permanece en Base64URL para verificación")
        print(f"  {signature_b64}")
        
        signature_bytes = self.decodificador.decodificar(signature_b64)
        print(f"  Tamaño: {len(signature_bytes)} bytes")
        
        return {
            'header': header,
            'payload': payload,
            'signature': signature_bytes,
            'header_b64': header_b64,
            'payload_b64': payload_b64,
            'signature_b64': signature_b64
        }
    
    def extraer_claims(self, payload):
        """
        Extrae y muestra claims del payload
        """
        print(f"\n{'='*60}")
        print("EXTRACCIÓN DE CLAIMS")
        print(f"{'='*60}")
        
        claims_estandar = ['iss', 'sub', 'aud', 'exp', 'nbf', 'iat', 'jti']
        claims_custom = []
        
        print("\nClaims estándar:")
        for claim in claims_estandar:
            if claim in payload:
                valor = payload[claim]
                print(f"  ✓ {claim}: {valor}")
                
                # Formatear timestamps
                if claim in ['exp', 'nbf', 'iat'] and isinstance(valor, int):
                    from datetime import datetime
                    fecha = datetime.fromtimestamp(valor)
                    print(f"     ({fecha})")
        
        print("\nClaims personalizados:")
        for claim, valor in payload.items():
            if claim not in claims_estandar:
                claims_custom.append(claim)
                print(f"  • {claim}: {valor}")
        
        if not claims_custom:
            print("  (ninguno)")
        
        return {
            'estandar': {k: payload[k] for k in claims_estandar if k in payload},
            'custom': {k: payload[k] for k in claims_custom}
        }


# Casos de prueba
if __name__ == "__main__":
    print("="*60)
    print("FASE 4: DECODIFICACIÓN DE JWT")
    print("="*60)
    
    # Crear un JWT de ejemplo
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": "auth.example.com",
        "sub": "1234567890",
        "name": "John Doe",
        "iat": 1516239022,
        "exp": 1516242622,
        "admin": True
    }
    signature_mock = b"signature_bytes_here"
    
    # Codificar
    decodificador = DecodificadorBase64URL()
    
    header_b64 = decodificador.codificar(json.dumps(header))
    payload_b64 = decodificador.codificar(json.dumps(payload))
    signature_b64 = decodificador.codificar(signature_mock)
    
    token_jwt = f"{header_b64}.{payload_b64}.{signature_b64}"
    
    print(f"\n\nJWT generado para prueba:")
    print(f"{token_jwt}")
    
    # Parsear
    parser = ParserJWT()
    componentes = parser.parsear(token_jwt)
    
    # Extraer claims
    claims = parser.extraer_claims(componentes['payload'])
    
    # Prueba con JWT real (ejemplo de internet)
    print("\n\n" + "="*60)
    print("PRUEBA CON JWT REAL")
    print("="*60)
    
    jwt_real = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    try:
        componentes_real = parser.parsear(jwt_real)
        claims_real = parser.extraer_claims(componentes_real['payload'])
        
        print("\n✓ JWT decodificado exitosamente")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
