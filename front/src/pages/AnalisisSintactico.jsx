import { useState } from "react"
import { useNavigate } from "react-router-dom"
import Navbar from "../components/Navbar"
import styles from "../styles/Admin.module.css"

/**
 * ANÁLISIS SINTÁCTICO DE JWT
 *
 * Gramática Formal (BNF):
 *
 * <JWT> ::= <Header> "." <Payload> "." <Signature>
 * <Header> ::= <Base64URLString>
 * <Payload> ::= <Base64URLString>
 * <Signature> ::= <Base64URLString>
 * <Base64URLString> ::= (<Base64URLChar>)+
 * <Base64URLChar> ::= [A-Za-z0-9_-]
 *
 * Autómata Finito Determinista (AFD):
 * Estados: {q0, q1, q2, q3, qError, qAccept}
 * Alfabeto: Σ = {Base64URLChar, '.'}
 *
 * Transiciones:
 * δ(q0, Base64URLChar) = q1  // Leyendo header
 * δ(q1, Base64URLChar) = q1  // Continuando header
 * δ(q1, '.') = q2            // Primer punto
 * δ(q2, Base64URLChar) = q3  // Leyendo payload
 * δ(q3, Base64URLChar) = q3  // Continuando payload
 * δ(q3, '.') = q4            // Segundo punto
 * δ(q4, Base64URLChar) = q5  // Leyendo signature
 * δ(q5, Base64URLChar) = q5  // Continuando signature
 *
 * Estado inicial: q0
 * Estado de aceptación: {q5}
 */

function AnalisisSintactico() {
  const navigate = useNavigate()
  const [jwt, setJwt] = useState("")
  const [result, setResult] = useState(null)

  /**
   * Validador sintáctico usando Autómata Finito Determinista
   */
  const validateSyntax = (token) => {
    const steps = []
    const errors = []

    // Verificar que no esté vacío
    if (!token || token.trim() === "") {
      return {
        valid: false,
        errors: ["Token vacío"],
        steps: ["Error: El token JWT no puede estar vacío"],
        structure: null,
      }
    }

    steps.push("Iniciando análisis sintáctico...")
    steps.push("Estado: q0 (inicial)")

    // Regex para Base64URL (sin padding '=')
    const base64UrlRegex = /^[A-Za-z0-9_-]+$/

    // División en tres partes
    const parts = token.split(".")

    steps.push(`Detectadas ${parts.length} partes separadas por '.'`)

    if (parts.length !== 3) {
      errors.push(
        `Error en δ(q1,'.'): Se esperan exactamente 3 partes, se encontraron ${parts.length}`
      )
      return {
        valid: false,
        errors,
        steps,
        structure: null,
      }
    }

    const [header, payload, signature] = parts

    // Validar Header (q0 -> q1)
    steps.push("Transición: δ(q0, Base64URLChar) → q1 (validando header)")
    if (!header || !base64UrlRegex.test(header)) {
      errors.push("Error en q1: Header no es una cadena Base64URL válida")
      errors.push(`Header recibido: "${header}"`)
      return { valid: false, errors, steps, structure: null }
    }
    steps.push(
      `✓ Header válido: ${header.substring(0, 20)}... (${
        header.length
      } caracteres)`
    )

    // Primer punto (q1 -> q2)
    steps.push("Transición: δ(q1, '.') → q2 (primer separador encontrado)")

    // Validar Payload (q2 -> q3)
    steps.push("Transición: δ(q2, Base64URLChar) → q3 (validando payload)")
    if (!payload || !base64UrlRegex.test(payload)) {
      errors.push("Error en q3: Payload no es una cadena Base64URL válida")
      errors.push(`Payload recibido: "${payload}"`)
      return { valid: false, errors, steps, structure: null }
    }
    steps.push(
      `✓ Payload válido: ${payload.substring(0, 20)}... (${
        payload.length
      } caracteres)`
    )

    // Segundo punto (q3 -> q4)
    steps.push("Transición: δ(q3, '.') → q4 (segundo separador encontrado)")

    // Validar Signature (q4 -> q5)
    steps.push("Transición: δ(q4, Base64URLChar) → q5 (validando signature)")
    if (!signature || !base64UrlRegex.test(signature)) {
      errors.push("Error en q5: Signature no es una cadena Base64URL válida")
      errors.push(`Signature recibida: "${signature}"`)
      return { valid: false, errors, steps, structure: null }
    }
    steps.push(
      `✓ Signature válida: ${signature.substring(0, 20)}... (${
        signature.length
      } caracteres)`
    )

    // Estado de aceptación
    steps.push("Estado final: q5 (ACEPTADO)")
    steps.push("✓ El token cumple con la gramática formal de JWT")

    return {
      valid: true,
      errors: [],
      steps,
      structure: {
        header: header,
        payload: payload,
        signature: signature,
        headerLength: header.length,
        payloadLength: payload.length,
        signatureLength: signature.length,
      },
    }
  }

  const handleAnalyze = () => {
    // Limpiar espacios en blanco del token antes de analizar
    const cleanedJwt = jwt.trim()
    const analysis = validateSyntax(cleanedJwt)
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
            <h1 className={styles.gradientTitle}>Análisis Sintáctico JWT</h1>
            <p>
              Validación de la estructura del token usando Autómata Finito
              Determinista (AFD)
            </p>

            <div style={{ marginBottom: 20, textAlign: "left" }}>
              <h3>Gramática Formal:</h3>
              <pre
                style={{
                  background: "#1e1e1e",
                  color: "#d4d4d4",
                  padding: "15px",
                  borderRadius: "5px",
                  overflow: "auto",
                }}
              >
                {`<JWT> ::= <Header> "." <Payload> "." <Signature>
<Header> ::= <Base64URLString>
<Payload> ::= <Base64URLString>
<Signature> ::= <Base64URLString>
<Base64URLString> ::= (<Base64URLChar>)+
<Base64URLChar> ::= [A-Za-z0-9_-]`}
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
                placeholder="Ingrese el token JWT completo (header.payload.signature)"
                rows={4}
                style={{
                  width: "100%",
                  padding: "10px",
                  fontFamily: "monospace",
                  fontSize: "14px",
                  border: "2px solid #4a90e2",
                  borderRadius: "5px",
                }}
              />
              <button
                onClick={handleAnalyze}
                style={{
                  marginTop: 10,
                  padding: "10px 20px",
                  background: "#4a90e2",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                }}
              >
                Analizar Sintaxis
              </button>
            </div>

            {result && (
              <div
                style={{
                  marginTop: 20,
                  padding: "20px",
                  background: result.valid ? "#d4edda" : "#f8d7da",
                  border: `2px solid ${result.valid ? "#28a745" : "#dc3545"}`,
                  borderRadius: "5px",
                }}
              >
                <h3 style={{ color: result.valid ? "#155724" : "#721c24" }}>
                  {result.valid ? "✓ SINTAXIS VÁLIDA" : "✗ SINTAXIS INVÁLIDA"}
                </h3>

                <div style={{ marginTop: 15 }}>
                  <h4>Pasos del Autómata:</h4>
                  <ol style={{ textAlign: "left", color: "#333" }}>
                    {result.steps.map((step, idx) => (
                      <li key={idx} style={{ marginBottom: 5 }}>
                        {step}
                      </li>
                    ))}
                  </ol>
                </div>

                {result.errors.length > 0 && (
                  <div style={{ marginTop: 15 }}>
                    <h4 style={{ color: "#721c24" }}>Errores detectados:</h4>
                    <ul style={{ textAlign: "left", color: "#721c24" }}>
                      {result.errors.map((error, idx) => (
                        <li key={idx}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.structure && (
                  <div style={{ marginTop: 15, textAlign: "left" }}>
                    <h4>Estructura detectada:</h4>
                    <pre
                      style={{
                        background: "#f8f9fa",
                        padding: "10px",
                        borderRadius: "5px",
                        overflow: "auto",
                      }}
                    >
                      {`Header:    ${result.structure.header.substring(
                        0,
                        40
                      )}... (${result.structure.headerLength} chars)
Payload:   ${result.structure.payload.substring(0, 40)}... (${
                        result.structure.payloadLength
                      } chars)
Signature: ${result.structure.signature.substring(0, 40)}... (${
                        result.structure.signatureLength
                      } chars)`}
                    </pre>
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

export default AnalisisSintactico
