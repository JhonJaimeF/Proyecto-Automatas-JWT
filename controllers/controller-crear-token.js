import jwt from "jsonwebtoken";

/**
 * @swagger
 * components:
 *   schemas:
 *     TokenCreado:
 *       type: object
 *       properties:
 *         mensaje:
 *           type: string
 *           example: "JWT creado exitosamente"
 *         token:
 *           type: string
 *           example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvIjoianVhbiIsInJvbCI6ImFkbWluIiwiaWF0IjoxNjg5MzQ1NjAwLCJleHAiOjE2ODkzNDkyMDB9.signature"
 *     
 *     ErrorCreacion:
 *       type: object
 *       properties:
 *         error:
 *           type: string
 *           example: "No se pudo crear el JWT"
 *         detalles:
 *           type: string
 *           example: "Mensaje de error específico"
 */

/**
 * @swagger
 * /api/token/crear:
 *   post:
 *     summary: Crear un nuevo JWT
 *     description: Genera un token JWT firmado con los datos proporcionados en el payload. El token tendrá una duración de 1 hora.
 *     tags: [Tokens]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               sub:
 *                 type: string
 *                 description: Nombre del usuario
 *                 example: "juan"
 *               email:
 *                 type: string
 *                 description: Email del usuario
 *                 example: "juan@ejemplo.com"
 *               role:
 *                 type: string
 *                 description: Rol del usuario
 *                 example: "admin"
 *             example:
 *               sub: "juan"
 *               email: "juan@ejemplo.com"
 *               role: "admin"
 *     responses:
 *       201:
 *         description: JWT creado exitosamente
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/TokenCreado'
 *       400:
 *         description: Datos inválidos en la solicitud
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Debes enviar un JSON con los datos del payload."
 *       500:
 *         description: Error interno del servidor
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorCreacion'
 */
export const crearJWT = (req, res) => {
  const datos = req.body;

  if (!datos || typeof datos !== "object") {
    return res.status(400).json({
      error: "Debes enviar un JSON con los datos del payload."
    });
  }

  try {
    const token = jwt.sign(
      datos,
      process.env.JWT_SECRET || "claveTemporal",
      { expiresIn: "1h" }
    );

    return res.status(201).json({
      mensaje: "JWT creado exitosamente",
      token
    });

  } catch (error) {
    return res.status(500).json({
      error: "No se pudo crear el JWT",
      detalles: error.message
    });
  }
};