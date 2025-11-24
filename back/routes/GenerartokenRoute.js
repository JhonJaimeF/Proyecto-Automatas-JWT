import { Router } from "express";
import { crearJWT } from "../controllers/controller-crear-token.js";

const router = Router();

router.post("/crear", crearJWT);

export default router;