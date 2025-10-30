import express from "express";
import cors from "cors";
import { generateJWT } from "./services/generateJWT.js";
import { verifyJWT } from "./services/verifyJWT.js";
import { decodeJWT } from "./services/decodeJWT.js";

const app = express();
app.use(cors());
app.use(express.json());

// Ruta: Generar JWT
app.post("/generate", (req, res) => {
  const { usuario, contrasena, role, iat } = req.body;
  if (!usuario || !contrasena || !role || iat === undefined) {
    return res.status(400).json({ error: "Faltan campos requeridos" });
  }

  try {
    const token = generateJWT({ usuario, role, iat });
    res.json({ jwt: token });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Ruta: Decodificar JWT
app.post("/decode", decodeJWT);

// Ruta: Verificar JWT
app.post("/verify", (req, res) => {
  const { token } = req.body;
  if (!token) return res.status(400).json({ error: "Token no proporcionado" });

  try {
    const verified = verifyJWT(token);
    res.json({ valid: true, payload: verified });
  } catch (error) {
    res.status(401).json({ valid: false, error: error.message });
  }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`✅ Servidor corriendo en http://localhost:${PORT}`));
