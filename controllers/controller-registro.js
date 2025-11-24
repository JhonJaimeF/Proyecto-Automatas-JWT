import jwt from "jsonwebtoken";
import Registro from "../models/Registro.js";

const MI_CLAVE_SECRETA = process.env.JWT_SECRET || "claveTemporal";

// Algoritmos permitidos
const ALGORITMOS_PERMITIDOS = ['HS256', 'HS384', 'HS512', 'RS256'];

// Función para decodificar Base64URL
const base64UrlDecode = (str, key) => {
  try {
    let base64 = str.replace(/-/g, '+').replace(/_/g, '/');
    const pad = base64.length % 4;
    if (pad) {
      if (pad === 1) throw new Error('InvalidBase64String: Padding inválido (longitud % 4 = 1)');
      base64 += new Array(5 - pad).join('=');
    }
    
    const buffer = Buffer.from(base64, 'base64');
    
    // Primero, verificar si es binario (no válido UTF-8)
    const decodedString = buffer.toString('utf8');
    const isValidUTF8 = Buffer.from(decodedString, 'utf8').equals(buffer);
    
    if (!isValidUTF8) {
      // Es binario, retornarlo como signature
      return {
        success: true,
        data: str,
        type: 'signature'
      };
    }
    
    // Si es válido UTF-8 (raw/text), proceder a verificar JSON
    let jsonObj;
    try {
      jsonObj = JSON.parse(decodedString);
      return {
        success: true,
        data: jsonObj,
        type: 'json'
      };
    } catch (jsonError) {
      // Si falla el JSON.parse, error como antes
      return {
        success: false,
        data: null,
        error: `JSONParseError: ${jsonError.message}`
      };
    }
    
  } catch (error) {
    // Errores generales (Base64, buffer, etc.)
    return {
      success: false,
      data: null,
      error: error.message || 'Error desconocido en decodificación Base64URL'
    };
  }
};

// Función para validar el header (refactorizada con regex)
const validarHeader = (header) => {
  const errores = [];

  // Validar que existan las propiedades
  if (!header.alg) {
    errores.push("Falta la propiedad 'alg' en el header");
    return { valido: false, errores };
  }

  if (!header.typ) {
    errores.push("Falta la propiedad 'typ' en el header");
    return { valido: false, errores };
  }

  // Validar 'typ' - debe ser exactamente "JWT"
  if (header.typ !== "JWT") {
    // Regex para detectar tipeos comunes en "JWT" (patrón: J/W/T en orden, longitud 2-4)
    const typTipeoRegex = /^[J|j][W|w][T|t](T?)?$/i;
    if (typTipeoRegex.test(header.typ)) {
      errores.push(`Error de tipeo en 'typ': se encontró '${header.typ}', debe ser 'JWT'`);
    } else {
      errores.push(`Valor inválido en 'typ': '${header.typ}', debe ser 'JWT'`);
    }
  }

  // Validar 'alg' - debe estar en la lista de algoritmos permitidos
  if (!ALGORITMOS_PERMITIDOS.includes(header.alg)) {
    // Regex para detectar tipeos en familias de algoritmos (HS y RS)
    const hsRegex = /^HS(25[56]?|38[4]?|51[2]?)$/i; // Captura HS255/6, HS38x, etc.
    const rsRegex = /^RS(25[56]?)$/i; // Captura RS255/6, etc.
    
    let sugerencia = null;
    if (hsRegex.test(header.alg)) {
      // Sugerir basado en el grupo capturado (grupo 1: el número)
      const numGrupo = header.alg.match(hsRegex)?.[1]?.toUpperCase() || '';
      if (numGrupo.startsWith('25')) sugerencia = 'HS256';
      else if (numGrupo.startsWith('38')) sugerencia = 'HS384';
      else if (numGrupo.startsWith('51')) sugerencia = 'HS512';
    } else if (rsRegex.test(header.alg)) {
      sugerencia = 'RS256'; // Común para RSxxx
    }

    if (sugerencia) {
      errores.push(`Error de tipeo en 'alg': se encontró '${header.alg}', probablemente querías '${sugerencia}'`);
    } else {
      errores.push(`Algoritmo no permitido: '${header.alg}'. Los algoritmos válidos son: ${ALGORITMOS_PERMITIDOS.join(', ')}`);
    }
  }

  return { valido: errores.length === 0, errores };
};

// Función para guardar en BD y responder
const guardarYResponder = async (estado, descripcion, res) => {
  try {
    const nuevoRegistro = await Registro.create({
      estado: estado,
      descripcion: descripcion
    });
    console.log(`Registro guardado - ID: ${nuevoRegistro.id_incremental}, Estado: ${estado}`);
  } catch (dbError) {
    console.error("❌ Error al guardar en BD:", dbError);
    return res.status(500).json({
      error: "Error al guardar el registro en la base de datos",
      detalles: dbError.message
    });
  }

  // Responder según el estado
  if (estado === "valido") {
    // VÁLIDO - Mostrar JSON completo para el frontend
    return res.status(200).json({
      estado: "valido",
      mensaje: "Token válido y no expirado",
      datos: {
        header: descripcion.header,
        payload: descripcion.payload,
        signature: descripcion.signature,
        claveSecreta: descripcion.claveSecreta,
        iat: descripcion.iat,
        exp: descripcion.exp
      }
    });
  } else if (estado === "invalido") {
    // INVÁLIDO - Distinguir entre expirado, clave incorrecta y otros errores
    if (descripcion.mensaje === "Token expirado") {
      // Token expirado - Mostrar datos completos
      return res.status(400).json({
        estado: "invalido",
        mensaje: "Token expirado",
        razon: "El token ha superado su fecha de expiración",
        datos: {
          header: descripcion.header,
          payload: descripcion.payload,
          signature: descripcion.signature,
          claveSecreta: descripcion.claveSecreta,
          iat: descripcion.iat,
          exp: descripcion.exp
        }
      });
    } else if (descripcion.mensaje === "Token no válido aún") {
      // Token con iat futuro - Mostrar datos completos
      return res.status(400).json({
        estado: "invalido",
        mensaje: "Token no válido aún",
        razon: "El token tiene una fecha de emisión (iat) en el futuro",
        datos: {
          header: descripcion.header,
          payload: descripcion.payload,
          signature: descripcion.signature,
          claveSecreta: descripcion.claveSecreta,
          iat: descripcion.iat,
          exp: descripcion.exp
        }
      });
    } else if (descripcion.mensaje === "Clave incorrecta") {
      // Clave incorrecta - Mostrar datos completos
      return res.status(400).json({
        estado: "invalido",
        mensaje: "Clave incorrecta",
        error: descripcion.error,
        datos: {
          header: descripcion.header,
          payload: descripcion.payload,
          signature: descripcion.signature,
          claveSecreta: descripcion.claveSecreta,
          iat: descripcion.iat,
          exp: descripcion.exp
        }
      });
    } else {
      // Otros errores de validez - Solo mostrar mensaje de error
      return res.status(400).json({
        estado: "invalido",
        mensaje: descripcion.mensaje || "Token inválido",
        error: descripcion.error
      });
    }
  } else {
    // CORRUPTO - Solo mensaje de error
    return res.status(400).json({
      estado: "corrupto",
      mensaje: "Token corrupto o malformado",
      error: descripcion.error
    });
  }
};

// Función para clasificar cada parte del JWT
const detectarTipoParte = (decoded) => {
  if (!decoded || typeof decoded !== 'object') return null;
  if (decoded.type === 'signature') return 'signature';
  
  const keys = Object.keys(decoded.data);
  
  // Claves típicas de header
  const headerKeys = ['alg', 'typ', 'kid', 'jku', 'x5u', 'x5c', 'x5t', 'cty'];
  const tieneHeaderKeys = keys.some(k => headerKeys.includes(k));
  
  // Claves típicas de payload
  const payloadKeys = ['sub', 'iss', 'aud', 'exp', 'nbf', 'iat', 'jti', 'name', 'email', 'role', 'usuario', 'id', 'data'];
  const tienePayloadKeys = keys.some(k => payloadKeys.includes(k));
  
  if (tieneHeaderKeys && !tienePayloadKeys) return 'header';
  if (tienePayloadKeys && !tieneHeaderKeys) return 'payload';
  if (tieneHeaderKeys && tienePayloadKeys) return 'mixto';
  
  // Si no tiene claves reconocibles pero tiene 'alg' es definitivamente header
  if (decoded.alg) return 'header';
  
  return 'desconocido';
};

export const verificarJWT = async (req, res) => {
  const { token, key } = req.body;

  if (!token || typeof token !== "string") {
    return res.status(400).json({
      error: "Debes enviar un 'token' en el body como string."
    });
  }

  if (key == null) {
    return res.status(400).json({
      error: "El campo 'key' es requerido en el body (puede ser una cadena vacía)."
    });
  }

  // Variables reutilizables para descripcion
  let estado = "corrupto";
  let tokenGuardado = token;
  let headerGuardado = null;
  let payloadGuardado = null;
  let signatureGuardado = null;
  let claveSecretaGuardada = null;
  let errorGuardado = null;
  let mensajeGuardado = null;
  let iatGuardado = null;
  let expGuardado = null;

  // VALIDAR ESTRUCTURA DEL TOKEN (debe tener exactamente 3 partes)
  const partes = token.split(".");
  if (partes.length !== 3) {
    estado = "invalido";
    errorGuardado = "Token mal formado - debe tener formato: header.payload.signature";
    mensajeGuardado = "Token incompleto, debe contener 3 partes separadas por puntos";

    return await guardarYResponder(estado, {
      token: tokenGuardado,
      signature: signatureGuardado,
      claveSecreta: claveSecretaGuardada,
      error: errorGuardado,
      partesEncontradas: partes.length,
      mensaje: mensajeGuardado
    }, res);
  }

  const erroresPartes = [];

  // Decodificar cada parte
  const [parte1, parte2, parte3] = partes;

  const decoded1 = base64UrlDecode(parte1);
  console.log("Decoded Parte 1:", decoded1);

  // Verificar la parte 1 del token
  if (!decoded1.success) {
    erroresPartes.push(`Error en la parte 1 del Token: ${decoded1.error}`);
  }

  const decoded2 = base64UrlDecode(parte2);
  console.log("Decoded Parte 2:", decoded2);
  
  // Verificar la parte 2 del token
  if (!decoded2.success) {
    erroresPartes.push(`Error en la parte 2 del Token: ${decoded2.error}`);
  } 

  const decoded3 = base64UrlDecode(parte3); 
  console.log("Decoded Parte 3:", decoded3);
  
  // Verificar la parte 3 del token
  if (!decoded3.success) {
    erroresPartes.push(`Error en la parte 3 del Token: ${decoded3.error}`);
  }

  if (erroresPartes.length > 0) {
    estado = "corrupto";
    headerGuardado = decoded1;
    payloadGuardado = decoded2;
    signatureGuardado = parte3;
    errorGuardado = erroresPartes.join(". ");
    mensajeGuardado = "Token corrupto - errores en la decodificación de las partes";

    return await guardarYResponder(estado, {
      token: tokenGuardado,
      header: headerGuardado,
      payload: payloadGuardado,
      signature: signatureGuardado,
      claveSecreta: claveSecretaGuardada,
      error: errorGuardado,
      mensaje: mensajeGuardado
    }, res);
  }

  // Detectar tipo de contenido de cada parte
  const tipo1 = detectarTipoParte(decoded1);
  const tipo2 = detectarTipoParte(decoded2);
  const tipo3 = detectarTipoParte(decoded3);

  console.log(`Tipos detectados - Parte 1: ${tipo1}, Parte 2: ${tipo2}, Parte 3: ${tipo3}`);

  // VALIDAR QUE LAS PARTES ESTÉN EN EL ORDEN CORRECTO
  const erroresOrden = [];
  
  // Validación de parte 1 -> debe ser el header
  if (tipo1 === 'payload') {
    erroresOrden.push("El Payload no debe ir en la posición del Header");
  }
  if (tipo1 === 'mixto') {
    erroresOrden.push("La primera parte contiene Claims de Header y Payload");
  }
  if (tipo1 === 'signature') {
    erroresOrden.push("No se logro decodificar la parte 1");
  }
  
  // Validación de parte 2 -> debe ser el payload
  if (tipo2 === 'header') {
    erroresOrden.push("El Header no debe ir en la posición del Payload");
  }
  if (tipo2 === 'mixto') {
    erroresOrden.push("La segunda parte contiene Claims de Header y Payload");
  }
  if (tipo2 === 'signature') {
    erroresOrden.push("No se logro decodificar la parte 2");
  }

  // Validación de parte 3 -> debe ser el signature
  if (decoded3.success && decoded3.type !== 'signature') {
    if (tipo3 === 'header') {
      erroresOrden.push("El Header no debe ir en la posición del Signature");
    } 
    if (tipo3 === 'payload') {
      erroresOrden.push("El Payload no debe ir en la posición del Signature");
    } 
    if (tipo3 === 'mixto') {
      erroresOrden.push("La tercera parte debe ser la firma, no contener estructura JSON");
    }
  }

  if (erroresOrden.length > 0) {
    estado = "invalido";
    headerGuardado = decoded1.data;
    payloadGuardado = decoded2.data;
    signatureGuardado = decoded3.data;
    errorGuardado = erroresOrden.join(". ");
    mensajeGuardado = "Token mal formado";

    return await guardarYResponder(estado, {
      token: tokenGuardado,
      header: headerGuardado,
      payload: payloadGuardado,
      signature: signatureGuardado,
      claveSecreta: claveSecretaGuardada,
      error: errorGuardado,
      mensaje: mensajeGuardado
    }, res);
  }

  // VALIDAR EL HEADER CON EXPRESIONES REGULARES
  if (decoded1.data) {
    const validacionHeader = validarHeader(decoded1.data);
    if (!validacionHeader.valido) {
      estado = "invalido";
      headerGuardado = decoded1;
      payloadGuardado = decoded2;
      signatureGuardado = parte3;
      errorGuardado = validacionHeader.errores.join(". ");
      mensajeGuardado = "Error en el header del token";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        error: errorGuardado,
        mensaje: mensajeGuardado
      }, res);
    }
  }

  // VALIDAR QUE EL HEADER SOLO CONTENGA INFORMACIÓN DE HEADER
  if (decoded1.data) {
    const headerKeys = Object.keys(decoded1.data);
    const invalidKeysInHeader = headerKeys.filter(key => {
      return ['sub', 'iss', 'aud', 'exp', 'nbf', 'iat', 'jti', 'name', 'email', 'role', 'usuario', 'id', 'data'].includes(key);
    });

    if (invalidKeysInHeader.length > 0) {
      estado = "invalido";
      headerGuardado = decoded1;
      payloadGuardado = decoded2;
      signatureGuardado = parte3;
      errorGuardado = `Header contiene información que no le corresponde: ${invalidKeysInHeader.join(', ')}`;
      mensajeGuardado = "Token mal formado";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        error: errorGuardado,
        mensaje: mensajeGuardado
      }, res);
    }
  }

  // VALIDAR QUE EL PAYLOAD SOLO CONTENGA INFORMACIÓN DE PAYLOAD
  if (decoded2.data) {
    const payloadKeys = Object.keys(decoded2.data);
    const invalidKeysInPayload = payloadKeys.filter(key => {
      return ['alg', 'typ', 'kid', 'jku'].includes(key);
    });

    if (invalidKeysInPayload.length > 0) {
      estado = "invalido";
      headerGuardado = decoded1;
      payloadGuardado = decoded2;
      signatureGuardado = parte3;
      errorGuardado = `Payload contiene información que no le corresponde: ${invalidKeysInPayload.join(', ')}`;
      mensajeGuardado = "Token mal formado";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        error: errorGuardado,
        mensaje: mensajeGuardado
      }, res);
    }
  }

  try {
    // Intentar decodificar con jwt.decode
    const decodificadoCompleto = jwt.decode(token, { complete: true });

    if (!decodificadoCompleto || !decodificadoCompleto.payload) {
      estado = "corrupto";
      errorGuardado = "Token corrupto - no se pudo decodificar el contenido";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        error: errorGuardado
      }, res);
    }

    const { header, payload, signature } = decodificadoCompleto;
    headerGuardado = header;
    payloadGuardado = payload;
    signatureGuardado = signature;

    const iat = payload.iat;
    const exp = payload.exp;
    const ahora = Math.floor(Date.now() / 1000);

    // VALIDAR QUE PAYLOAD TENGA CONTENIDO
    if (!payload || Object.keys(payload).length === 0) {
      estado = "invalido";
      errorGuardado = "Payload vacío o mal formado";
      mensajeGuardado = "Token mal formado";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        error: errorGuardado,
        mensaje: mensajeGuardado
      }, res);
    }

    // VALIDAR QUE SIGNATURE EXISTA Y NO ESTÉ VACÍA
    if (!signature || signature.trim() === "") {
      estado = "invalido";
      errorGuardado = "Signature vacía o mal formada";
      mensajeGuardado = "Token mal formado";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        error: errorGuardado,
        mensaje: mensajeGuardado
      }, res);
    }

    // VALIDAR IAT (issued at) - no debe ser en el futuro
    if (iat && typeof iat === 'number') {
      if (iat > ahora) {
        estado = "invalido";
        mensajeGuardado = "Token no válido aún";
        iatGuardado = new Date(iat * 1000).toISOString();
        expGuardado = exp ? new Date(exp * 1000).toISOString() : null;

        return await guardarYResponder(estado, {
          token: tokenGuardado,
          header: headerGuardado,
          payload: payloadGuardado,
          signature: signatureGuardado,
          claveSecreta: claveSecretaGuardada,
          iat: iatGuardado,
          exp: expGuardado,
          mensaje: mensajeGuardado
        }, res);
      }
    }

    // Verificar si el token está vencido (EXP)
    const tokenVencido = exp && exp < ahora;

    iatGuardado = iat ? new Date(iat * 1000).toISOString() : null;
    expGuardado = exp ? new Date(exp * 1000).toISOString() : null;

    if (tokenVencido) {
      estado = "invalido";
      mensajeGuardado = "Token expirado";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        iat: iatGuardado,
        exp: expGuardado,
        mensaje: mensajeGuardado
      }, res);
    }

    // Siempre validar la firma con la clave proporcionada
    try {
      jwt.verify(token, key, { algorithms: ALGORITMOS_PERMITIDOS });
      // Verificación exitosa
      estado = "valido";
      mensajeGuardado = "Token válido y no expirado";
      claveSecretaGuardada = key;

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: claveSecretaGuardada,
        iat: iatGuardado,
        exp: expGuardado,
        mensaje: mensajeGuardado
      }, res);
    } catch (verifyError) {
      // Verificación fallida - clave incorrecta (incluyendo clave vacía)
      estado = "invalido";
      errorGuardado = "Clave incorrecta";
      mensajeGuardado = "Clave incorrecta";

      return await guardarYResponder(estado, {
        token: tokenGuardado,
        header: headerGuardado,
        payload: payloadGuardado,
        signature: signatureGuardado,
        claveSecreta: null,
        iat: iatGuardado,
        exp: expGuardado,
        error: errorGuardado,
        mensaje: mensajeGuardado
      }, res);
    }

  } catch (error) {
    estado = "corrupto";
    errorGuardado = "Token corrupto - " + error.message;

    return await guardarYResponder(estado, {
      token: tokenGuardado,
      signature: signatureGuardado,
      claveSecreta: claveSecretaGuardada,
      error: errorGuardado
    }, res);
  }
};

/**
 * @swagger
 * components:
 *   schemas:
 *     TokenValido:
 *       type: object
 *       properties:
 *         estado:
 *           type: string
 *           example: "valido"
 *         mensaje:
 *           type: string
 *           example: "Token válido y no expirado"
 *         datos:
 *           type: object
 *           properties:
 *             header:
 *               type: object
 *               properties:
 *                 alg:
 *                   type: string
 *                   example: "HS256"
 *                 typ:
 *                   type: string
 *                   example: "JWT"
 *             payload:
 *               type: object
 *               properties:
 *                 usuario:
 *                   type: string
 *                   example: "juan"
 *                 email:
 *                   type: string
 *                   example: "juan@ejemplo.com"
 *                 iat:
 *                   type: number
 *                   example: 1732276800
 *                 exp:
 *                   type: number
 *                   example: 1732280400
 *             signature:
 *               type: string
 *               example: "abc123xyz..."
 *             claveSecreta:
 *               type: string
 *               nullable: true
 *               example: "claveTemporal"
 *             iat:
 *               type: string
 *               format: date-time
 *               example: "2024-11-22T10:00:00.000Z"
 *             exp:
 *               type: string
 *               format: date-time
 *               example: "2024-11-22T11:00:00.000Z"
 *             esNuestroToken:
 *               type: boolean
 *               example: true
 *     
 *     TokenExpirado:
 *       type: object
 *       properties:
 *         estado:
 *           type: string
 *           example: "invalido"
 *         mensaje:
 *           type: string
 *           example: "Token expirado"
 *         razon:
 *           type: string
 *           example: "El token ha superado su fecha de expiración"
 *         datos:
 *           type: object
 *           properties:
 *             header:
 *               type: object
 *             payload:
 *               type: object
 *             signature:
 *               type: string
 *             claveSecreta:
 *               type: string
 *               nullable: true
 *             iat:
 *               type: string
 *               format: date-time
 *             exp:
 *               type: string
 *               format: date-time
 *             esNuestroToken:
 *               type: boolean
 *     
 *     TokenInvalido:
 *       type: object
 *       properties:
 *         estado:
 *           type: string
 *           example: "invalido"
 *         mensaje:
 *           type: string
 *           example: "Error en el header del token"
 *         error:
 *           type: string
 *           example: "Error de tipeo en 'typ': se encontró 'JTW', debe ser 'JWT'"
 *     
 *     TokenCorrupto:
 *       type: object
 *       properties:
 *         estado:
 *           type: string
 *           example: "corrupto"
 *         mensaje:
 *           type: string
 *           example: "Token corrupto o malformado"
 *         error:
 *           type: string
 *           example: "Token corrupto - jwt malformed"
 */

/**
 * @swagger
 * /api/token/verificar:
 *   post:
 *     summary: Verificar un token JWT
 *     description: |
 *       Valida y verifica un token JWT con las siguientes comprobaciones:
 *       
 *       **Validaciones realizadas:**
 *       - Estructura correcta (header.payload.signature)
 *       - Orden correcto de las partes
 *       - Header con algoritmo válido (HS256, HS384, HS512, RS256)
 *       - Tipo de token correcto (JWT)
 *       - Detección de errores de tipeo en alg y typ
 *       - Contenido apropiado en cada sección
 *       - Verificación de expiración (exp)
 *       - Identificación de clave secreta (si coincide con la del servidor)
 *       
 *       **Estados posibles:**
 *       - **válido**: Token decodificado correctamente y no expirado
 *       - **inválido**: Token con errores de formato, tipeo, o expirado
 *       - **corrupto**: Token que no se puede decodificar
 *       
 *       **Nota:** Se registran TODOS los intentos en la base de datos
 *     tags: [Tokens]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - token
 *             properties:
 *               token:
 *                 type: string
 *                 description: Token JWT a verificar
 *                 example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c3VhcmlvIjoianVhbiIsImVtYWlsIjoianVhbkBlamVtcGxvLmNvbSIsImlhdCI6MTczMjI3NjgwMCwiZXhwIjoxNzMyMjgwNDAwfQ.signature"
 *     responses:
 *       200:
 *         description: Token válido y no expirado
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/TokenValido'
 *       400:
 *         description: Token inválido, expirado o corrupto
 *         content:
 *           application/json:
 *             oneOf:
 *               - $ref: '#/components/schemas/TokenExpirado'
 *               - $ref: '#/components/schemas/TokenInvalido'
 *               - $ref: '#/components/schemas/TokenCorrupto'
 *             examples:
 *               expirado:
 *                 summary: Token expirado
 *                 value:
 *                   estado: "invalido"
 *                   mensaje: "Token expirado"
 *                   razon: "El token ha superado su fecha de expiración"
 *                   datos:
 *                     header: { "alg": "HS256", "typ": "JWT" }
 *                     payload: { "usuario": "juan", "iat": 1705000000, "exp": 1705003600 }
 *                     signature: "xyz789..."
 *                     claveSecreta: null
 *                     iat: "2024-01-12T10:00:00.000Z"
 *                     exp: "2024-01-12T11:00:00.000Z"
 *                     esNuestroToken: false
 *               errorTipeo:
 *                 summary: Error de tipeo en header
 *                 value:
 *                   estado: "invalido"
 *                   mensaje: "Error en el header del token"
 *                   error: "Error de tipeo en 'typ': se encontró 'JTW', debe ser 'JWT'"
 *               algoritmoInvalido:
 *                 summary: Algoritmo no permitido
 *                 value:
 *                   estado: "invalido"
 *                   mensaje: "Error en el header del token"
 *                   error: "Algoritmo no permitido: 'HS128'. Los algoritmos válidos son: HS256, HS384, HS512, RS256"
 *               ordenIncorrecto:
 *                 summary: Partes en orden incorrecto
 *                 value:
 *                   estado: "invalido"
 *                   mensaje: "Token mal formado"
 *                   error: "El payload no debe ir en la posición del header. El header no debe ir en la posición del payload"
 *               corrupto:
 *                 summary: Token corrupto
 *                 value:
 *                   estado: "corrupto"
 *                   mensaje: "Token corrupto o malformado"
 *                   error: "Token corrupto - jwt malformed"
 *       500:
 *         description: Error al guardar en la base de datos
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: "Error al guardar el registro en la base de datos"
 *                 detalles:
 *                   type: string
 *                   example: "Mensaje de error específico"
 */