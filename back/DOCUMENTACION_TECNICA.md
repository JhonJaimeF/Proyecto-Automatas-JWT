# Documentación Técnica: Analizador y Validador de JWT

## Aplicación de Conceptos de Lenguajes Formales

### 1. Autómatas Finitos Deterministas (AFD)

#### 1.1 Validación de Estructura JWT

**Lenguaje reconocido**: L = {w | w = header.payload.signature, donde cada parte es Base64URL}

**AFD formal**:

- **Q** = {q0, q1, q2, q3, q4, q5} (estados)
- **Σ** = {A-Z, a-z, 0-9, -, \_, .} (alfabeto Base64URL + punto)
- **q0** = estado inicial
- **F** = {q5} (estados finales)
- **δ**: función de transición

```
Estados:
- q0: Inicial (esperando header)
- q1: Leyendo header (Base64URL)
- q2: Primer punto leído
- q3: Leyendo payload (Base64URL)
- q4: Segundo punto leído
- q5: Leyendo signature (Base64URL) - ESTADO FINAL
```

**Tabla de transiciones** (simplificada):

```
δ(q0, Base64URL) → q1
δ(q1, Base64URL) → q1
δ(q1, '.') → q2
δ(q2, Base64URL) → q3
δ(q3, Base64URL) → q3
δ(q3, '.') → q4
δ(q4, Base64URL) → q5
δ(q5, Base64URL) → q5
```

**Implementación**: `automatas/afd_base.py` - función `crear_afd_jwt_estructura()`

#### 1.2 Validación de Base64URL

**Lenguaje reconocido**: L = {w | w ∈ {A-Z, a-z, 0-9, -, \_}+}

Este AFD verifica que todos los caracteres pertenezcan al alfabeto Base64URL.

**Implementación**: `automatas/afd_base.py` - función `crear_afd_base64url()`

---

### 2. Autómatas Finitos No Deterministas (AFN)

#### 2.1 Validación de Múltiples Formatos de Timestamp

El AFN permite reconocer **múltiples formatos** de timestamp mediante no-determinismo:

**Formatos aceptados**:

1. Unix timestamp: dígitos puros (e.g., "1516239022")
2. ISO 8601: YYYY-MM-DD (e.g., "2025-10-23")

**AFN con ε-transiciones**:

```
      ε
q0 ----→ q1 → q1 → q1 → ... (dígitos puros)
  |
  └ε→ q2 → q3 → q4 → q5 → q6 (YYYY-MM-DD)
```

Desde el estado inicial q0, hay **dos ε-transiciones** que conducen a ramas diferentes:

- Una rama acepta solo dígitos (timestamp Unix)
- Otra rama acepta el formato ISO con guiones

**Algoritmo de procesamiento**:

1. Calcular ε-clausura del estado inicial
2. Para cada símbolo:
   - Calcular conjunto de estados alcanzables
   - Calcular ε-clausura del resultado
3. Aceptar si algún estado final es alcanzado

**Implementación**: `automatas/afn_base.py` - función `crear_afn_timestamp_formats()`

---

### 3. Minimización de AFD

**Algoritmo de partición de estados**:

1. **Partición inicial**: Separar estados finales de no finales

   - P0 = {F, Q - F}

2. **Refinamiento iterativo**: Para cada partición P:

   - Dos estados p, q están en la misma partición si:
     - Para todo símbolo a ∈ Σ: δ(p, a) y δ(q, a) están en la misma partición

3. **Construcción del AFD mínimo**:
   - Cada partición final → un estado en el AFD mínimo
   - Transiciones basadas en representantes

**Ejemplo**:

```
AFD Original (6 estados):
q0, q1, q2, q3, q4, q5

Partición inicial:
P0 = {{q2}, {q0, q1, q3, q4, q5}}  (q2 es final)

Refinamiento:
P1 = {{q2}, {q0, q3, q4}, {q1}, {q5}}

Estados inalcanzables eliminados:
q5 (inalcanzable)

AFD Mínimo (4 estados):
P0, P1, P2, P3
```

**Implementación**: `automatas/minimizador.py` - clase `MinimizadorAFD`

---

### 4. Construcción de Thompson (Expresión Regular → AFN)

#### 4.1 Construcción para Operaciones Básicas

**Operaciones soportadas**:

1. **Símbolo simple (a)**:

```
q0 --a--> q1
```

2. **Concatenación (r1·r2)**:

```
[AFN1] --ε--> [AFN2]
```

3. **Unión (r1|r2)**:

```
       ε → [AFN1] → ε
      ↗                ↘
q0 →                    → qf
      ↘                ↗
       ε → [AFN2] → ε
```

4. **Clausura de Kleene (r\*)**:

```
    ┌──── ε ────┐
    ↓           │
    ε → [AFN] → ε → qf
q0 →             ↗
    └──── ε ────┘
```

5. **Clausura positiva (r+)**:

```
r+ = r·r*
```

#### 4.2 Ejemplo: Validación de Dominio en JWT

**Expresión Regular**: `(letra)+·'.'·(letra)+`

**Proceso de construcción**:

1. Construir AFN para cada letra
2. Aplicar clausura positiva (r+)
3. Construir AFN para '.'
4. Concatenar: letras+ · '.' · letras+

**Aplicaciones en JWT**:

- Validar formato de emails (`user@domain.com`)
- Validar URLs (`https://example.com`)
- Validar identificadores únicos

**Implementación**: `automatas/clausula.py` - clase `ConstructorThompson`

---

### 5. Aplicación en las Fases del Proyecto

#### Fase 3: Análisis Semántico

**Autómata de Estados Temporales**:

Estados conceptuales para validación de expiración:

```
FUTURO (exp > now)     → Token válido
PRESENTE (exp = now)   → En límite (advertencia)
PASADO (exp < now)     → Token expirado (error)
```

**Validaciones usando autómatas**:

- Tipos de datos (AFD que acepta solo tipos válidos)
- Coherencia temporal (autómata de estados)
- Algoritmos válidos (AFD que reconoce HS256, HS384, etc.)

**Implementación**: `fase3_analisis_semantico/validador_semantico.py`

#### Fase 4: Decodificación

**Proceso como autómata**:

```
Input (JWT) → [Parser] → [AFD validador] → [Decodificador Base64] → Output (JSON)
```

Cada etapa puede modelarse como autómata:

- Parser: AFD que reconoce estructura A.B.C
- Decodificador: Transductor finito (AFD con salida)

**Implementación**: `fase4_decodificacion/decodificador_jwt.py`

#### Fase 5: Codificación

**Generación como autómata transductor**:

```
Input (JSON) → [Codificador Base64] → [Firmador HMAC] → Output (JWT)
```

El proceso de firma HMAC puede verse como:

- Entrada: mensaje + clave
- Proceso: función de transición basada en hash
- Salida: firma digital

**Implementación**: `fase5_codificacion/generador_jwt.py`

---

## Gramáticas y Expresiones Regulares

### Gramática para JWT

**Gramática libre de contexto**:

```
JWT → Header '.' Payload '.' Signature
Header → Base64URL
Payload → Base64URL
Signature → Base64URL
Base64URL → (Letra | Dígito | '-' | '_')+
Letra → 'a' | 'b' | ... | 'z' | 'A' | ... | 'Z'
Dígito → '0' | '1' | ... | '9'
```

### Expresiones Regulares Equivalentes

**Estructura JWT completa**:

```regex
^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$
```

**Base64URL**:

```regex
^[A-Za-z0-9_-]+$
```

**Email en claims**:

```regex
^[a-z0-9]+@[a-z0-9]+\.[a-z]+$
```

---

## Teoremas y Propiedades Aplicados

### 1. Teorema de Kleene

**Enunciado**: Un lenguaje es regular si y solo si puede ser reconocido por un autómata finito.

**Aplicación**:

- La estructura JWT es regular → se puede validar con AFD
- Los formatos Base64URL son regulares → AFD suficiente

### 2. Equivalencia AFD-AFN

**Propiedad**: Para todo AFN existe un AFD equivalente.

**Aplicación**:

- Usamos AFN para expresar patrones complejos con facilidad
- Podríamos convertir a AFD para optimizar (algoritmo de construcción de subconjuntos)

### 3. Minimización de AFD

**Teorema**: Para todo AFD existe un AFD mínimo equivalente único (salvo isomorfismo).

**Aplicación**:

- Optimizar el validador de estructura JWT
- Reducir memoria y tiempo de procesamiento

### 4. Construcción de Thompson

**Propiedad**: Toda expresión regular puede convertirse en un AFN equivalente.

**Aplicación**:

- Definir patrones complejos con ER
- Construir AFN automáticamente
- Validar claims con patrones flexibles

---

## Complejidad Computacional

### Análisis de Complejidad

| Operación                | Complejidad | Justificación            |
| ------------------------ | ----------- | ------------------------ |
| Validar estructura (AFD) | O(n)        | Recorrer cadena una vez  |
| Decodificar Base64URL    | O(n)        | Procesar cada carácter   |
| Validar semántica        | O(k)        | k = número de claims     |
| Verificar firma HMAC     | O(n)        | n = longitud del mensaje |
| Minimizar AFD            | O(n² log n) | n = número de estados    |
| Thompson (ER→AFN)        | O(m)        | m = longitud de ER       |

### Optimizaciones

1. **AFD vs AFN**: Usar AFD para validación rápida
2. **Minimización**: Reducir estados para mejorar rendimiento
3. **Tabla de símbolos**: Hash table para claims (O(1) lookup)

---

## Diagramas de Autómatas

### AFD: Estructura JWT

```
     Base64URL           '.'         Base64URL
q0 ──────────→ q1 ──────────→ q2 ──────────→ q3
               │                              │
               └─ Base64URL ─→ q1            └─ '.' ─→ q4
                                                        │
                                                        │ Base64URL
                                                        ↓
                                                       q5 ⭕
                                                        │
                                                        └─ Base64URL ─→ q5
```

### AFN: Múltiples Formatos

```
         ε              dígito
q0 ──────────→ q1 ──────────────→ q1 ⭕
 │                              ↺
 │
 │      ε          dígito×4      '-'
 └──────────→ q2 ──────────→ q6 ─────→ q7 ⭕
```

---

## Referencias Teóricas

1. **Teoría de Autómatas**: Hopcroft, Motwani, Ullman - "Introduction to Automata Theory"
2. **Expresiones Regulares**: Construcción de Thompson (1968)
3. **Minimización**: Algoritmo de Hopcroft (1971)
4. **JWT**: RFC 7519 - JSON Web Token
5. **Base64URL**: RFC 4648 - The Base16, Base32, and Base64 Data Encodings

---

## Conclusiones

Este proyecto demuestra la aplicación práctica de:

✅ **AFD**: Validación eficiente de estructuras regulares  
✅ **AFN**: Reconocimiento de patrones con no-determinismo  
✅ **Minimización**: Optimización de autómatas  
✅ **Construcción de Thompson**: Conversión ER↔AFN  
✅ **Clausuras**: Operaciones de lenguajes regulares

Todos los conceptos teóricos de Lenguajes Formales se aplican directamente a la validación y generación de JSON Web Tokens.
