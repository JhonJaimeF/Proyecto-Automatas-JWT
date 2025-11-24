import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';
import swaggerUI from 'swagger-ui-express';
import swaggerSpec from './swagger.js';
import connectDB from './drivers/conectDB.js';
import rutaCrearToken from "./routes/GenerartokenRoute.js";
import rutaVerificarToken from "./routes/VerificartokenRoute.js";

//Inicializaciones
const app = express();
dotenv.config();


//Conexion a la base de datos
connectDB();

// Configurar Swagger
//setupSwagger(app);

//Middlewares
app.set('PORT', process.env.PORT || 5000);
app.use(express.json());
app.use(cors());
app.use('/docs', swaggerUI.serve, swaggerUI.setup(swaggerSpec));


//Rutas
app.use("/api/token", rutaCrearToken);
app.use("/api/token", rutaVerificarToken);

app.listen(app.get('PORT'), () => 
  console.log(`Server Ready at http://localhost:${app.get('PORT')}`)
);