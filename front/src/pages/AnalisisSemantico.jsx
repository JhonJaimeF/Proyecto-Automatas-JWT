import { useState } from "react"
import { useNavigate } from "react-router-dom"
import Navbar from "../components/Navbar"
import styles from "../styles/Admin.module.css"

/**
 * ANÁLISIS SEMÁNTICO DE JWT
 *
 * Reglas Semánticas Formales:
 *
 * 1. Validación de Tipos de Datos:
 *    - iat (Issued At): ℕ (número entero positivo, timestamp UNIX)
 *    - exp (Expiration): ℕ (número entero positivo, timestamp UNIX)
 *    - nbf (Not Before): ℕ (número entero positivo, timestamp UNIX)
 *    - sub (Subject): String ∈ Σ* donde Σ = {a-zA-Z0-9@._-}
 *    - iss (Issuer): String ∈ Σ*
 *    - aud (Audience): String | Array<String>
 *
 * 2. Restricciones Temporales:
 *    - iat ≤ exp (la emisión debe ser antes de la expiración)
 *    - nbf ≤ exp (not-before debe ser antes de expiración)
 *    - now ≥ iat (el token no puede ser del futuro)
 *    - now < exp (el token no debe estar expirado)
 *    - now ≥ nbf (el token ya debe ser válido)
 *
 * 3. Validación de Claims Obligatorios:
 *    - Para tokens de autenticación: {sub, iat, exp} ⊆ Claims
 *    - Para tokens de usuario: {userId, role} ⊆ Claims
 *
 * 4. Validación de Valores:
 *    - role ∈ {'admin', 'user', 'guest'}
 *    - exp - iat ≤ 86400 (máximo 24 horas de validez)
 *    - userId > 0 (ID positivo)
 *
 * Sistema de Tipos:
 * τ ::= Number | String | Boolean | Object | Array | Null
 * Γ ::= {claim₁: τ₁, claim₂: τ₂, ..., claimₙ: τₙ}
 */

function AnalisisSemantico() {
  const navigate = useNavigate()
  const [jwt, setJwt] = useState("")
  const [result, setResult] = useState(null)

  /**
   * Decodifica Base64URL a objeto JSON
   */
  const decodeBase64URL = (str) => {
    try {
      // Convertir Base64URL a Base64 estándar
      let base64 = str.replace(/-/g, "+").replace(/_/g, "/")
      // Agregar padding si es necesario
      while (base64.length % 4 !== 0) {
        base64 += "="
      }
      const decoded = atob(base64)
      return JSON.parse(decoded)
    } catch (error) {
      throw new Error(`Error decodificando Base64URL: ${error.message}`)
    }
  }

  /**
   * Validador semántico con reglas formales
   */
  const validateSemantics = (token) => {
    const checks = []
    const warnings = []
    const errors = []

    try {
      // Extraer partes del token
      const parts = token.split(".")
      if (parts.length !== 3) {
        return {
          valid: false,
          errors: ["Error sintáctico: el token debe tener 3 partes"],
          checks: [],
          warnings: [],
          payload: null,
        }
      }

      // Decodificar header y payload
      const header = decodeBase64URL(parts[0])
      const payload = decodeBase64URL(parts[1])

      checks.push("✓ Token decodificado exitosamente")

      // REGLA 1: Validación del algoritmo en header
      checks.push("\n=== VALIDACIÓN DE HEADER ===")
      if (!header.alg) {
        errors.push(
          'Error semántico: Header debe contener el claim "alg" (algoritmo)'
        )
      } else if (typeof header.alg !== "string") {
        errors.push(
          `Error de tipo: "alg" debe ser String, se encontró ${typeof header.alg}`
        )
      } else {
        const validAlgorithms = [
          "HS256",
          "HS384",
          "HS512",
          "RS256",
          "RS384",
          "RS512",
          "ES256",
          "ES384",
          "ES512",
        ]
        if (!validAlgorithms.includes(header.alg)) {
          warnings.push(`Advertencia: Algoritmo "${header.alg}" no es estándar`)
        } else {
          checks.push(
            `✓ Algoritmo válido: ${header.alg} ∈ {HS256, HS384, HS512, RS256, ...}`
          )
        }
      }

      if (header.typ && header.typ !== "JWT") {
        warnings.push(`Advertencia: El tipo "${header.typ}" no es "JWT"`)
      }

      // REGLA 2: Validación de tipos de datos en payload
      checks.push("\n=== VALIDACIÓN DE TIPOS DE DATOS ===")

      const now = Math.floor(Date.now() / 1000)

      // Validar iat (Issued At)
      if (payload.iat !== undefined) {
        if (typeof payload.iat !== "number" || !Number.isInteger(payload.iat)) {
          errors.push(
            `Error de tipo: "iat" debe ser Number (entero), se encontró ${typeof payload.iat}`
          )
        } else if (payload.iat < 0) {
          errors.push(
            'Error de valor: "iat" debe ser un timestamp UNIX positivo (iat ∈ ℕ)'
          )
        } else if (payload.iat > now + 300) {
          errors.push(
            'Error temporal: "iat" no puede ser del futuro (now ≥ iat)'
          )
        } else {
          checks.push(
            `✓ iat: ${payload.iat} ∈ ℕ (${new Date(
              payload.iat * 1000
            ).toLocaleString()})`
          )
        }
      } else {
        warnings.push('Advertencia: Falta claim "iat" (Issued At)')
      }

      // Validar exp (Expiration)
      if (payload.exp !== undefined) {
        if (typeof payload.exp !== "number" || !Number.isInteger(payload.exp)) {
          errors.push(
            `Error de tipo: "exp" debe ser Number (entero), se encontró ${typeof payload.exp}`
          )
        } else if (payload.exp < 0) {
          errors.push(
            'Error de valor: "exp" debe ser un timestamp UNIX positivo (exp ∈ ℕ)'
          )
        } else {
          checks.push(
            `✓ exp: ${payload.exp} ∈ ℕ (${new Date(
              payload.exp * 1000
            ).toLocaleString()})`
          )

          if (payload.exp < now) {
            errors.push(
              `Error temporal: Token expirado (now < exp). Expiró hace ${Math.floor(
                (now - payload.exp) / 60
              )} minutos`
            )
          } else {
            checks.push(
              `✓ Token no expirado: now (${now}) < exp (${payload.exp})`
            )
          }
        }
      } else {
        warnings.push('Advertencia: Falta claim "exp" (Expiration Time)')
      }

      // REGLA 3: Relaciones temporales
      if (payload.iat !== undefined && payload.exp !== undefined) {
        checks.push("\n=== VALIDACIÓN DE RESTRICCIONES TEMPORALES ===")
        if (payload.iat > payload.exp) {
          errors.push(
            "Error semántico: iat > exp (el token está emitido después de expirar)"
          )
        } else {
          checks.push(
            `✓ Restricción temporal: iat (${payload.iat}) ≤ exp (${payload.exp})`
          )
        }

        const duration = payload.exp - payload.iat
        checks.push(`Duración del token: ${Math.floor(duration / 3600)} horas`)
        if (duration > 86400) {
          warnings.push(
            `Advertencia: Duración > 24 horas (exp - iat = ${duration}s)`
          )
        }
      }

      // Validar nbf (Not Before)
      if (payload.nbf !== undefined) {
        if (typeof payload.nbf !== "number" || !Number.isInteger(payload.nbf)) {
          errors.push(
            `Error de tipo: "nbf" debe ser Number (entero), se encontró ${typeof payload.nbf}`
          )
        } else {
          if (payload.nbf > now) {
            errors.push(
              `Error temporal: Token no válido todavía (now ≥ nbf). Será válido en ${Math.floor(
                (payload.nbf - now) / 60
              )} minutos`
            )
          } else {
            checks.push(
              `✓ Token ya válido: now (${now}) ≥ nbf (${payload.nbf})`
            )
          }

          if (payload.exp !== undefined && payload.nbf > payload.exp) {
            errors.push("Error semántico: nbf > exp (nunca será válido)")
          }
        }
      }

      // REGLA 4: Validación de claims estándar
      checks.push("\n=== VALIDACIÓN DE CLAIMS ESTÁNDAR ===")

      if (payload.sub !== undefined) {
        if (typeof payload.sub !== "string") {
          errors.push(
            `Error de tipo: "sub" debe ser String, se encontró ${typeof payload.sub}`
          )
        } else if (!/^[a-zA-Z0-9@._-]+$/.test(payload.sub)) {
          warnings.push('Advertencia: "sub" contiene caracteres no estándar')
        } else {
          checks.push(`✓ sub: "${payload.sub}" ∈ String (formato válido)`)
        }
      }

      if (payload.iss !== undefined) {
        if (typeof payload.iss !== "string") {
          errors.push(
            `Error de tipo: "iss" debe ser String, se encontró ${typeof payload.iss}`
          )
        } else {
          checks.push(`✓ iss: "${payload.iss}" ∈ String`)
        }
      }

      if (payload.aud !== undefined) {
        if (typeof payload.aud !== "string" && !Array.isArray(payload.aud)) {
          errors.push(
            `Error de tipo: "aud" debe ser String | Array<String>, se encontró ${typeof payload.aud}`
          )
        } else {
          checks.push(
            `✓ aud: ${JSON.stringify(payload.aud)} ∈ (String | Array<String>)`
          )
        }
      }

      // REGLA 5: Validación de claims personalizados
      if (payload.role !== undefined) {
        checks.push("\n=== VALIDACIÓN DE CLAIMS PERSONALIZADOS ===")
        const validRoles = ["admin", "user", "guest"]
        if (!validRoles.includes(payload.role)) {
          errors.push(
            `Error de valor: "role" debe ser ∈ {admin, user, guest}, se encontró "${payload.role}"`
          )
        } else {
          checks.push(`✓ role: "${payload.role}" ∈ {admin, user, guest}`)
        }
      }

      if (payload.userId !== undefined) {
        if (typeof payload.userId !== "number") {
          errors.push(
            `Error de tipo: "userId" debe ser Number, se encontró ${typeof payload.userId}`
          )
        } else if (payload.userId <= 0) {
          errors.push(
            `Error de valor: "userId" debe ser > 0, se encontró ${payload.userId}`
          )
        } else {
          checks.push(`✓ userId: ${payload.userId} ∈ ℕ⁺ (número positivo)`)
        }
      }

      // REGLA 6: Verificar claims obligatorios mínimos
      checks.push("\n=== VALIDACIÓN DE COMPLETITUD ===")
      const requiredClaims = ["iat", "exp"]
      const missingClaims = requiredClaims.filter(
        (claim) => payload[claim] === undefined
      )

      if (missingClaims.length > 0) {
        warnings.push(
          `Advertencia: Faltan claims recomendados: {${missingClaims.join(
            ", "
          )}}`
        )
      } else {
        checks.push(
          `✓ Claims obligatorios presentes: {${requiredClaims.join(
            ", "
          )}} ⊆ Payload`
        )
      }

      return {
        valid: errors.length === 0,
        errors,
        warnings,
        checks,
        header,
        payload,
        metadata: {
          totalClaims: Object.keys(payload).length,
          isExpired: payload.exp && payload.exp < now,
          isNotYetValid: payload.nbf && payload.nbf > now,
          timeToExpiry: payload.exp ? Math.max(0, payload.exp - now) : null,
        },
      }
    } catch (error) {
      return {
        valid: false,
        errors: [`Error crítico: ${error.message}`],
        warnings: [],
        checks: [],
        header: null,
        payload: null,
      }
    }
  }

  const handleAnalyze = () => {
    const analysis = validateSemantics(jwt)
    setResult(analysis)
  }

  const handleBack = () => {
    navigate("/", { replace: true })
  }

  return (
    <div className={styles.adminLayout}>
      <Navbar />
      <main className={styles.mainContent}>
        <div className={styles.pagePattern}>
          <div className={styles.inner}>
            <h1 className={styles.gradientTitle}>Análisis Semántico JWT</h1>
            <p>
              Validación del significado y coherencia del contenido del token
            </p>

            <div style={{ marginBottom: 20, textAlign: "left" }}>
              <h3>Reglas Semánticas:</h3>
              <pre
                style={{
                  background: "#1e1e1e",
                  color: "#d4d4d4",
                  padding: "15px",
                  borderRadius: "5px",
                  overflow: "auto",
                  fontSize: "12px",
                }}
              >
                {`1. Tipos de Datos:
   - iat, exp, nbf ∈ ℕ (números enteros positivos)
   - sub, iss ∈ String
   - aud ∈ (String | Array<String>)

2. Restricciones Temporales:
   - now ≥ iat (no del futuro)
   - now < exp (no expirado)
   - now ≥ nbf (ya válido)
   - iat ≤ exp (coherencia temporal)
   
3. Valores Válidos:
   - role ∈ {admin, user, guest}
   - userId > 0
   - alg ∈ {HS256, RS256, ES256, ...}`}
              </pre>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label
                style={{
                  display: "block",
                  marginBottom: 10,
                  fontWeight: "bold",
                }}
              >
                Token JWT a analizar:
              </label>
              <textarea
                value={jwt}
                onChange={(e) => setJwt(e.target.value)}
                placeholder="Ingrese el token JWT completo para análisis semántico"
                rows={4}
                style={{
                  width: "100%",
                  padding: "10px",
                  fontFamily: "monospace",
                  fontSize: "14px",
                  border: "2px solid #9b59b6",
                  borderRadius: "5px",
                }}
              />
              <button
                onClick={handleAnalyze}
                style={{
                  marginTop: 10,
                  padding: "10px 20px",
                  background: "#9b59b6",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                }}
              >
                Analizar Semántica
              </button>
            </div>

            {result && (
              <div
                style={{
                  marginTop: 20,
                  padding: "20px",
                  background: result.valid ? "#d4edda" : "#fff3cd",
                  border: `2px solid ${result.valid ? "#28a745" : "#ffc107"}`,
                  borderRadius: "5px",
                }}
              >
                <h3 style={{ color: result.valid ? "#155724" : "#856404" }}>
                  {result.valid
                    ? "✓ SEMÁNTICA VÁLIDA"
                    : "⚠ PROBLEMAS SEMÁNTICOS DETECTADOS"}
                </h3>

                {result.errors.length > 0 && (
                  <div
                    style={{
                      marginTop: 15,
                      padding: "10px",
                      background: "#f8d7da",
                      borderRadius: "5px",
                    }}
                  >
                    <h4 style={{ color: "#721c24" }}>Errores Semánticos:</h4>
                    <ul style={{ textAlign: "left", color: "#721c24" }}>
                      {result.errors.map((error, idx) => (
                        <li key={idx}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.warnings.length > 0 && (
                  <div
                    style={{
                      marginTop: 15,
                      padding: "10px",
                      background: "#fff3cd",
                      borderRadius: "5px",
                    }}
                  >
                    <h4 style={{ color: "#856404" }}>Advertencias:</h4>
                    <ul style={{ textAlign: "left", color: "#856404" }}>
                      {result.warnings.map((warning, idx) => (
                        <li key={idx}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div style={{ marginTop: 15 }}>
                  <h4>Verificaciones Realizadas:</h4>
                  <pre
                    style={{
                      textAlign: "left",
                      background: "#f8f9fa",
                      padding: "15px",
                      borderRadius: "5px",
                      fontSize: "13px",
                      whiteSpace: "pre-wrap",
                      color: "#333",
                    }}
                  >
                    {result.checks.join("\n")}
                  </pre>
                </div>

                {result.payload && (
                  <div style={{ marginTop: 15, textAlign: "left" }}>
                    <h4>Payload Decodificado:</h4>
                    <pre
                      style={{
                        background: "#1e1e1e",
                        color: "#d4d4d4",
                        padding: "15px",
                        borderRadius: "5px",
                        overflow: "auto",
                      }}
                    >
                      {JSON.stringify(result.payload, null, 2)}
                    </pre>
                  </div>
                )}

                {result.metadata && (
                  <div style={{ marginTop: 15, textAlign: "left" }}>
                    <h4>Metadatos:</h4>
                    <ul style={{ color: "#333" }}>
                      <li>Total de claims: {result.metadata.totalClaims}</li>
                      <li>
                        Estado:{" "}
                        {result.metadata.isExpired
                          ? "❌ Expirado"
                          : result.metadata.isNotYetValid
                          ? "⏳ No válido aún"
                          : "✅ Activo"}
                      </li>
                      {result.metadata.timeToExpiry !== null && (
                        <li>
                          Tiempo hasta expiración:{" "}
                          {Math.floor(result.metadata.timeToExpiry / 60)}{" "}
                          minutos
                        </li>
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <div style={{ marginTop: 20 }}>
              <button onClick={handleBack} className={styles.logoutBtn}>
                Volver al Inicio
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default AnalisisSemantico
