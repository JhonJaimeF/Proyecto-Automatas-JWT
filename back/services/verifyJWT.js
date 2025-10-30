import jwt from "jsonwebtoken";
import { SECRET_KEY } from "../config/secret.js";

/**
 * Verifica la validez de un token JWT.
 * @param {String} token - Token a verificar
 * @returns {Object} Payload verificado
 */
export function verifyJWT(token) {
  try {
    const verified = jwt.verify(token, SECRET_KEY);
    return verified;
  } catch (error) {
    throw new Error("Token inválido: " + error.message);
  }
}
