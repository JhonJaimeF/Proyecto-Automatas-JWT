# Proyecto Final LF 2025-2: Analizador y Validador de JWT

## Adelanto Fases 3, 4 y 5

Este adelanto implementa las fases de análisis semántico, decodificación y codificación de JSON Web Tokens aplicando conceptos de **Lenguajes Formales** y **Teoría de Autómatas**.

## Estructura del Proyecto

```
AvanceProyecto/
├── fase3_analisis_semantico/
│   ├── automata_validador.py       # AFD para validación de estructura
│   ├── validador_campos.py         # Validación semántica con autómatas
│   └── expresiones_regulares.py    # Conversión AF ↔ ER
├── fase4_decodificacion/
│   ├── base64url_decoder.py        # Decodificador Base64URL
│   ├── parser_json.py              # Parser con autómatas
│   └── extractor_claims.py         # Extracción de claims
├── fase5_codificacion/
│   ├── base64url_encoder.py        # Codificador Base64URL
│   ├── generador_json.py           # Generador JSON
│   └── firmador.py                 # Algoritmos de firma
├── automatas/
│   ├── afd_base.py                 # Implementación AFD
│   ├── afn_base.py                 # Implementación AFN
│   ├── minimizador.py              # Minimización de AFD
│   └── clausula.py                 # Clausura de Thompson
└── tests/
    └── test_jwt.py                 # Suite de pruebas

```

## Aplicación de Conceptos de Lenguajes Formales

### 1. AFD (Autómata Finito Determinista)

- Validación de formato JWT (3 partes separadas por puntos)
- Validación de caracteres Base64URL válidos
- Verificación de tipos de datos en claims

### 2. AFN (Autómata Finito No Determinista)

- Análisis de patrones en claims
- Validación de múltiples formatos de fechas

### 3. AFD Mínimo Equivalente

- Optimización del autómata de validación
- Reducción de estados en el parser

### 4. Conversión AF ↔ Expresión Regular

- Generación de expresiones regulares desde autómatas
- Construcción de autómatas desde expresiones (Clausura de Thompson)

## Instalación y Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python tests/test_jwt.py

# Ejecutar validador completo
python main.py
```

## Casos de Prueba Implementados

✓ Tokens válidos con diferentes algoritmos (HS256, HS384, RS256)  
✓ Tokens expirados  
✓ Tokens con firma inválida  
✓ Tokens malformados (sintaxis incorrecta)  
✓ Tokens con claims faltantes  
✓ Tokens con tipos de datos incorrectos

## Autores

Proyecto Final - Lenguajes Formales 2025-2
