# Guía de Uso - Analizador y Validador de JWT

## Instalación

```bash
# Navegar al directorio del proyecto
cd "c:\Users\User\Downloads\lenguajes formales\AvanceProyecto"

# Instalar dependencias
pip install -r requirements.txt
```

## Ejemplos de Uso

### 1. Ejecutar el Programa Principal

```bash
# Menú interactivo
python main.py

# Analizar un JWT específico
python main.py --token "eyJhbGci..." --clave "mi_clave_secreta"

# Ejecutar casos de prueba
python main.py --demo
```

### 2. Probar Autómatas Individualmente

#### AFD - Validación de Estructura JWT

```bash
python automatas/afd_base.py
```

**Salida esperada**:

```
AFD para validación de estructura JWT
================================
Pruebas de validación:
1. 'eyJhbGc.eyJzdWI.SflKxw'
   ✓ ACEPTADO: Cadena aceptada
```

#### AFN - Validación de Patrones

```bash
python automatas/afn_base.py
```

#### Minimización de AFD

```bash
python automatas/minimizador.py
```

**Salida esperada**:

```
Minimización de AFD
====================
Estados: 6 → 4
Reducción: 33.3%
```

#### Construcción de Thompson

```bash
python automatas/clausula.py
```

### 3. Fase 3: Análisis Semántico

```bash
python fase3_analisis_semantico/validador_semantico.py
```

**Ejemplo de validación**:

```python
from fase3_analisis_semantico.validador_semantico import ValidadorSemanticoJWT

validador = ValidadorSemanticoJWT()

header = {
    "alg": "HS256",
    "typ": "JWT"
}

payload = {
    "iss": "auth.example.com",
    "sub": "user123",
    "exp": 1730000000,
    "iat": 1729996400
}

validador.validar_header(header)
validador.validar_payload(payload)
validador.generar_reporte()
```

### 4. Fase 4: Decodificación

```bash
python fase4_decodificacion/decodificador_jwt.py
```

**Ejemplo de uso**:

```python
from fase4_decodificacion.decodificador_jwt import ParserJWT

parser = ParserJWT()

jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

componentes = parser.parsear(jwt)

print(f"Header: {componentes['header']}")
print(f"Payload: {componentes['payload']}")
```

### 5. Fase 5: Codificación y Firma

```bash
python fase5_codificacion/generador_jwt.py
```

**Ejemplo de generación**:

```python
from fase5_codificacion.generador_jwt import GeneradorJWT
from datetime import datetime

generador = GeneradorJWT(algoritmo='HS256')

payload = generador.crear_payload(
    issuer="auth.universidad.edu",
    subject="estudiante123",
    expiracion_minutos=60,
    claims_custom={
        "nombre": "Juan Pérez",
        "carrera": "Ingeniería"
    }
)

clave_secreta = "mi_clave_super_secreta"
token = generador.generar_token(payload, clave_secreta)

print(f"JWT: {token}")

# Verificar firma
es_valido = generador.verificar_firma(token, clave_secreta)
print(f"Firma válida: {es_valido}")
```

### 6. Suite Completa de Pruebas

```bash
python tests/test_jwt.py
```

**Salida esperada**:

```
SUITE DE PRUEBAS - Proyecto JWT
================================

test_afd_estructura_jwt_valida ... ok
test_header_valido ... ok
test_generar_token ... ok
...

Tests ejecutados: 20
Éxitos: 20
Fallos: 0
Errores: 0
```

## Casos de Prueba Detallados

### Caso 1: Token Válido

```python
# Generar token válido
from fase5_codificacion.generador_jwt import GeneradorJWT
from datetime import datetime

gen = GeneradorJWT()
payload = {
    "iss": "auth.example.com",
    "sub": "user123",
    "exp": int(datetime.now().timestamp()) + 3600,
    "iat": int(datetime.now().timestamp()),
    "nombre": "Usuario Prueba",
    "rol": "admin"
}

token = gen.generar_token(payload, "clave123")

# Analizar
from main import AnalizadorValidadorJWT
analizador = AnalizadorValidadorJWT()
resultado = analizador.analizar_completo(token, "clave123")

# Resultado esperado: ✓ VALIDACIÓN EXITOSA
```

### Caso 2: Token Expirado

```python
payload_expirado = {
    "iss": "auth.service",
    "exp": int(datetime.now().timestamp()) - 1000,  # Expirado
    "iat": int(datetime.now().timestamp()) - 5000
}

token = gen.generar_token(payload_expirado, "clave123")
resultado = analizador.analizar_completo(token, "clave123")

# Resultado esperado: ✗ Token expirado
```

### Caso 3: Firma Inválida

```python
payload = {"sub": "user"}
token = gen.generar_token(payload, "clave_correcta")

# Verificar con clave incorrecta
resultado = analizador.analizar_completo(token, "clave_incorrecta")

# Resultado esperado: ✗ FIRMA INVÁLIDA
```

### Caso 4: Sintaxis Incorrecta

```python
token_malformado = "header.payload"  # Solo 2 partes

# Resultado esperado: ✗ JWT inválido: debe tener 3 partes
```

### Caso 5: Claims con Tipos Incorrectos

```python
payload_invalido = {
    "iss": 12345,  # Debe ser string
    "exp": "2025-10-23",  # Debe ser int
    "sub": True  # Debe ser string
}

# Resultado esperado: ✗ Errores de tipo
```

## Aplicaciones de Autómatas

### 1. AFD: Validación Rápida

**Ventaja**: O(n) - procesa cada carácter una sola vez

```python
from automatas.afd_base import crear_afd_jwt_estructura

afd = crear_afd_jwt_estructura()

# Validar miles de tokens eficientemente
tokens = ["header.payload.sig", "invalid", "a.b.c"]
for token in tokens:
    aceptado, msg = afd.procesar(token)
    print(f"{token}: {aceptado}")
```

### 2. AFN: Flexibilidad con Múltiples Patrones

**Ventaja**: Expresar patrones complejos con no-determinismo

```python
from automatas.afn_base import crear_afn_timestamp_formats

afn = crear_afn_timestamp_formats()

# Acepta múltiples formatos
timestamps = ["1516239022", "2025-10-23"]
for ts in timestamps:
    aceptado, _ = afn.procesar(ts)
    print(f"{ts}: {'✓' if aceptado else '✗'}")
```

### 3. Minimización: Optimización

**Ventaja**: Reducir estados para mejorar rendimiento

```python
from automatas.minimizador import MinimizadorAFD

# Minimizar un AFD con estados redundantes
minimizador = MinimizadorAFD(afd_no_minimo)
afd_optimizado = minimizador.minimizar()

# Resultado: mismo lenguaje, menos estados
```

### 4. Construcción de Thompson: ER → AFN

**Ventaja**: Definir patrones con expresiones regulares

```python
from automatas.clausula import ConstructorThompson

constructor = ConstructorThompson()

# ER: a|b (acepta 'a' o 'b')
afn = constructor.desde_expresion_simple('a|b')

# ER: a* (cero o más 'a')
afn_estrella = constructor.desde_expresion_simple('a*')

# ER: a+ (una o más 'a')
afn_positiva = constructor.desde_expresion_simple('a+')
```

## Análisis de Rendimiento

### Benchmark

```python
import time

# 1000 validaciones con AFD
inicio = time.time()
for _ in range(1000):
    afd.procesar("header.payload.signature")
tiempo_afd = time.time() - inicio

print(f"AFD: {tiempo_afd:.4f} segundos")
# Resultado esperado: < 0.01 segundos
```

## Troubleshooting

### Error: "Módulo no encontrado"

```bash
# Asegurar que está en el directorio correcto
cd "c:\Users\User\Downloads\lenguajes formales\AvanceProyecto"

# Verificar estructura
dir
```

### Error: "Símbolo no válido"

**Causa**: Carácter no Base64URL en el token

**Solución**: Verificar que solo contenga A-Z, a-z, 0-9, -, \_

### Error: "Token expirado"

**Causa**: Claim 'exp' es menor que el tiempo actual

**Solución**: Generar token con expiración futura

## Extensiones Futuras

### 1. Soporte RSA/ECDSA

```python
# Implementar algoritmos asimétricos
class GeneradorJWT_RSA(GeneradorJWT):
    def firmar_rsa(self, mensaje, clave_privada):
        # Implementar firma RSA
        pass
```

### 2. Conversión AFN → AFD

```python
# Algoritmo de construcción de subconjuntos
def afn_to_afd(afn):
    # Implementar conversión
    pass
```

### 3. Expresiones Regulares Complejas

```python
# Soportar paréntesis y precedencia
# ER: (a|b)*c
constructor.desde_expresion_compleja('(a|b)*c')
```

## Recursos Adicionales

- **Documentación Técnica**: `DOCUMENTACION_TECNICA.md`
- **Código Fuente**: Ver comentarios en cada archivo
- **Tests**: `tests/test_jwt.py`

## Contacto y Soporte

Para preguntas sobre el proyecto:

- Revisar la documentación técnica
- Ejecutar casos de prueba
- Consultar los comentarios en el código

---

**¡Éxito con tu proyecto de Lenguajes Formales!** 🎓
