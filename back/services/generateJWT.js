import jwt from "jsonwebtoken";
import { SECRET_KEY } from "../config/secret.js";

/**
 * Genera un JWT con los datos proporcionados.
 * @param {Object} payload - Información a incluir en el token
 * @param {String} [expiresIn="1h"] - Tiempo de expiración
 * @returns {String} Token generado
 */
// En tu función generateJWT o en el endpoint /generate
export function generateJWT(payload, expiresIn = "1h") {
  try {
    // Convertimos iat a número válido (segundos UNIX)
    const sanitizedPayload = {
      ...payload,
      iat: Math.floor(Number(payload.iat)) || Math.floor(Date.now() / 1000),
    };

    const token = jwt.sign(sanitizedPayload, SECRET_KEY, {
      algorithm: "HS256",
      expiresIn,
    });
    return token;
  } catch (error) {
    throw new Error("Error al generar el token: " + error.message);
  }
}

