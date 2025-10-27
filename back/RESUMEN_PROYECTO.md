# 🎓 Proyecto Final: Analizador y Validador de JWT

## Lenguajes Formales 2025-2

---

## 📋 Resumen Ejecutivo

Este proyecto implementa un **Analizador y Validador completo de JSON Web Tokens (JWT)** aplicando **TODOS** los conceptos fundamentales de Lenguajes Formales y Teoría de Autómatas.

### ✨ Conceptos Aplicados

| Concepto                  | Aplicación en JWT                                     | Archivo                    |
| ------------------------- | ----------------------------------------------------- | -------------------------- |
| **AFD**                   | Validación de estructura header.payload.signature     | `automatas/afd_base.py`    |
| **AFN**                   | Validación de patrones múltiples (timestamps, emails) | `automatas/afn_base.py`    |
| **AFD Mínimo**            | Optimización del validador                            | `automatas/minimizador.py` |
| **Construcción Thompson** | Conversión ER → AFN para patrones                     | `automatas/clausula.py`    |
| **Expresiones Regulares** | Definición de patrones Base64URL                      | `automatas/clausula.py`    |

---

## 🏗️ Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────────────┐
│                    ANALIZADOR JWT                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐           │
│  │  FASE 3  │      │  FASE 4  │      │  FASE 5  │           │
│  │ Análisis │ ───▶ │Decodific.│ ───▶ │Codificac.│          │
│  │Semántico │      │          │      │  y Firma │           │
│  └──────────┘      └──────────┘      └──────────┘           │
│       │                 │                  │                │
│       ▼                 ▼                  ▼                │
│  ┌────────────────────────────────────────────┐            │
│  │          AUTÓMATAS FINITOS                 │            │
│  ├────────────────────────────────────────────┤            │
│  │  • AFD (Validación rápida)                │            │
│  │  • AFN (Patrones complejos)               │            │
│  │  • AFD Mínimo (Optimización)              │            │
│  │  • Thompson (ER ↔ AFN)                    │            │
│  └────────────────────────────────────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura Completa

```
AvanceProyecto/
│
├── 📖 README.md                          # Descripción general
├── 📖 DOCUMENTACION_TECNICA.md           # Teoría formal completa
├── 📖 GUIA_USO.md                        # Ejemplos prácticos
│
├── 🤖 automatas/                         # Teoría de autómatas
│   ├── afd_base.py                      # AFD + ejemplos JWT
│   ├── afn_base.py                      # AFN + ε-transiciones
│   ├── minimizador.py                   # Algoritmo de minimización
│   └── clausula.py                      # Construcción de Thompson
│
├── 🔍 fase3_analisis_semantico/         # Validación semántica
│   └── validador_semantico.py           # AFD para tipos y coherencia
│
├── 📦 fase4_decodificacion/             # Decodificación
│   └── decodificador_jwt.py             # Base64URL + Parser
│
├── 🔐 fase5_codificacion/               # Codificación y firma
│   └── generador_jwt.py                 # HMAC-SHA256/384/512
│
├── 🧪 tests/                            # Suite completa de pruebas
│   └── test_jwt.py                      # 20+ tests unitarios
│
├── 🚀 main.py                           # Programa principal
├── 🎭 demo_interactiva.py               # Demostración guiada
└── 📦 requirements.txt                  # Dependencias
```

---

## 🎯 Fases del Proyecto

### Fase 3: Análisis Semántico ✅

**Objetivo**: Validar la estructura lógica y semántica del JWT

**Conceptos aplicados**:

- ✓ AFD para validar algoritmos permitidos
- ✓ Autómata de estados temporales (validación de expiración)
- ✓ Tabla de símbolos para claims
- ✓ Validación de tipos de datos

**Características**:

```python
✓ Campos obligatorios (alg, typ)
✓ Tipos de datos correctos (iss: string, exp: int)
✓ Validación temporal (exp, nbf, iat)
✓ Coherencia entre claims
✓ Detección de algoritmos inseguros
```

---

### Fase 4: Decodificación ✅

**Objetivo**: Extraer y decodificar componentes del JWT

**Conceptos aplicados**:

- ✓ AFD para validar estructura (3 partes)
- ✓ Decodificador Base64URL (transductor)
- ✓ Parser JSON

**Proceso**:

```
JWT (string) → [Parser] → [AFD Validador] → [Base64 Decoder] → JSON (objetos)
```

**Funcionalidades**:

```python
✓ Separación header.payload.signature
✓ Decodificación Base64URL → JSON
✓ Extracción de claims estándar
✓ Extracción de claims personalizados
✓ Manejo de padding Base64
```

---

### Fase 5: Codificación ✅

**Objetivo**: Generar JWT firmados desde objetos JSON

**Conceptos aplicados**:

- ✓ Codificador Base64URL
- ✓ Firma HMAC (HS256, HS384, HS512)
- ✓ Generación de claims temporales

**Proceso**:

```
JSON (objetos) → [Base64 Encoder] → [HMAC Signer] → JWT (string firmado)
```

**Funcionalidades**:

```python
✓ Generación de header y payload
✓ Codificación Base64URL
✓ Firma HMAC-SHA256/384/512
✓ Verificación de firma
✓ Claims temporales automáticos
```

---

## 🤖 Autómatas Implementados

### 1. AFD: Estructura JWT

**Lenguaje**: L = {header.payload.signature}

```
Estados: q0 → q1 → q2 → q3 → q4 → q5
         (inicio) (header) (.) (payload) (.) (signature)
```

**Complejidad**: O(n) - lineal en longitud del token

---

### 2. AFN: Múltiples Formatos

**Lenguaje**: L = {timestamps Unix} ∪ {timestamps ISO}

```
       ε
q0 ────→ q1 (Unix: solo dígitos)
  |
  └─ε─→ q2 (ISO: YYYY-MM-DD)
```

**Ventaja**: No-determinismo permite flexibilidad

---

### 3. AFD Mínimo

**Algoritmo**: Partición de estados equivalentes

**Reducción típica**: 30-50% menos estados

```
Original: 6 estados → Mínimo: 4 estados
Ganancia: 33% optimización
```

---

### 4. Construcción de Thompson

**Operaciones**:

| ER       | Construcción      | Uso en JWT         |
| -------- | ----------------- | ------------------ |
| `a`      | Símbolo simple    | Caracteres Base64  |
| `r1·r2`  | Concatenación     | header.payload     |
| `r1\|r2` | Unión             | Múltiples formatos |
| `r*`     | Clausura Kleene   | Repeticiones       |
| `r+`     | Clausura positiva | Al menos uno       |

---

## 📊 Casos de Prueba

### ✅ Tokens Válidos

```python
✓ JWT con HS256
✓ JWT con HS384
✓ JWT con HS512
✓ Claims estándar correctos
✓ Claims personalizados
✓ Firma válida
```

### ❌ Tokens Inválidos

```python
✗ Token expirado (exp < now)
✗ Token no válido aún (nbf > now)
✗ Firma incorrecta
✗ Algoritmo no soportado
✗ Estructura malformada (2 partes)
✗ Tipos de datos incorrectos
```

---

## 🚀 Inicio Rápido

### 1. Instalación

```bash
cd "c:\Users\User\Downloads\lenguajes formales\AvanceProyecto"
pip install -r requirements.txt
```

### 2. Demostración Interactiva

```bash
python demo_interactiva.py
```

### 3. Pruebas Automáticas

```bash
python tests/test_jwt.py
```

### 4. Programa Principal

```bash
python main.py
```

---

## 🎓 Aplicación de Conceptos Teóricos

### Lenguajes Regulares

- ✅ Base64URL es regular → AFD suficiente
- ✅ Estructura JWT es regular → AFD eficiente
- ✅ Minimización reduce estados

### Conversiones

- ✅ **ER → AFN**: Construcción de Thompson
- ✅ **AFN → AFD**: Posible con algoritmo de subconjuntos
- ✅ **AFD → AFD Mínimo**: Algoritmo de partición

### Propiedades

- ✅ **Clausura bajo unión**: r1 | r2
- ✅ **Clausura bajo concatenación**: r1 · r2
- ✅ **Clausura de Kleene**: r\*
- ✅ **Determinismo vs No-determinismo**: Ambos implementados

---

## 📈 Análisis de Complejidad

| Operación     | Complejidad | Justificación          |
| ------------- | ----------- | ---------------------- |
| Validar AFD   | O(n)        | Un estado por símbolo  |
| Procesar AFN  | O(n·m)      | n símbolos, m estados  |
| Minimizar AFD | O(n² log n) | Refinamiento iterativo |
| Thompson      | O(m)        | m = longitud de ER     |
| Decodificar   | O(n)        | Procesar cada byte     |
| Firmar HMAC   | O(n)        | Hash de mensaje        |

---

## 🏆 Características Destacadas

### Innovación

✨ **Integración completa** de teoría y práctica  
✨ **Autómatas reales** aplicados a JWT  
✨ **Optimización** con minimización  
✨ **Flexibilidad** con AFN

### Calidad de Código

✅ **Documentación completa** en cada módulo  
✅ **Tests exhaustivos** (20+ casos)  
✅ **Ejemplos interactivos**  
✅ **Manejo de errores** robusto

### Pedagogía

📚 **Comentarios explicativos** detallados  
📚 **Demostración paso a paso**  
📚 **Visualización de autómatas**  
📚 **Documentación técnica formal**

---

## 📚 Referencias

1. **Hopcroft, Motwani, Ullman** - "Introduction to Automata Theory, Languages, and Computation"
2. **RFC 7519** - JSON Web Token (JWT)
3. **RFC 4648** - Base64 Data Encodings
4. **Thompson (1968)** - Regular Expression Search Algorithm
5. **Hopcroft (1971)** - An n log n Algorithm for Minimizing States

---

## ✅ Checklist del Proyecto

### Requerimientos Cumplidos

- [x] **Aplicar teoría de lenguajes formales** → AFD, AFN, ER
- [x] **Implementar analizador léxico** → Base64URL, tokens
- [x] **Construir parser sintáctico** → Estructura JWT
- [x] **Realizar análisis semántico** → Tipos, validación temporal
- [x] **Implementar decodificación** → Base64URL decoder
- [x] **Implementar codificación** → Base64URL encoder + HMAC
- [x] **Aplicar criptografía** → Firma digital HMAC
- [x] **AFD implementado** → Validación de estructura
- [x] **AFN implementado** → Patrones múltiples
- [x] **AFD mínimo equivalente** → Optimización
- [x] **AF ↔ Expresión Regular** → Construcción de Thompson
- [x] **Clausura (Kleene)** → Operaciones con ER

---

## 🎯 Conclusión

Este proyecto demuestra la **aplicación práctica completa** de:

✅ Autómatas Finitos Deterministas (AFD)  
✅ Autómatas Finitos No Deterministas (AFN)  
✅ Minimización de autómatas  
✅ Construcción de Thompson  
✅ Expresiones regulares  
✅ Análisis léxico, sintáctico y semántico  
✅ Codificación y decodificación  
✅ Criptografía (HMAC)

Todo aplicado al **mundo real**: JSON Web Tokens (JWT) utilizados en millones de aplicaciones web.

---

## 👨‍💻 Ejecución

```bash
# Demostración interactiva (RECOMENDADO)
python demo_interactiva.py

# Suite de pruebas
python tests/test_jwt.py

# Programa principal
python main.py

# Autómatas individuales
python automatas/afd_base.py
python automatas/afn_base.py
python automatas/minimizador.py
python automatas/clausula.py
```

---

## 📞 Soporte

Para cualquier duda:

1. Revisa `DOCUMENTACION_TECNICA.md`
2. Consulta `GUIA_USO.md`
3. Ejecuta `demo_interactiva.py`
4. Revisa los comentarios en el código

---

**¡Proyecto completo y funcional!** 🎉

_Lenguajes Formales 2025-2_
