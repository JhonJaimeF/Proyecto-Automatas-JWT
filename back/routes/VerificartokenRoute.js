import { Router } from "express";
import { verificarJWT } from "../controllers/controller-registro.js";

const router = Router();

router.post("/verificar", verificarJWT);

export default router;