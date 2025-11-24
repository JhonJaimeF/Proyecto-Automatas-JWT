import jwt from "jsonwebtoken";
import { SECRET_KEY } from "../config/secret.js";

/**
 * Decodifica un JWT sin verificar su validez (solo lectura del payload).
 */
export function decodeJWT(req, res) {
  const token = req.body.jwt; // Simplifica: el frontend siempre envía 'jwt'

  if (!token) {
    return res.status(400).json({ error: "JWT no proporcionado" });
  }

  try {
    // Solo decodifica, sin verificar firma
    const decoded = jwt.decode(token);

    if (!decoded) {
      return res.status(400).json({ error: "No se pudo decodificar el JWT." });
    }

    // Retorna el payload directamente (sin envolver en { decoded })
    res.json(decoded);
  } catch (error) {
    res.status(500).json({ error: "Error al decodificar: " + error.message });
  }
}