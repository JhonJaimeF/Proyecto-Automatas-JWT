import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'API de Verificación y Generación de JWT',
      version: '1.0.0',
      description: 'API para crear y verificar tokens JWT con validaciones exhaustivas',
      contact: {
        name: 'Soporte API',
        email: 'soporte@ejemplo.com'
      }
    },
    servers: [
      {
        url: 'http://localhost:5000',
        description: 'Servidor de desarrollo'
      },
      {
        url: 'https://api.ejemplo.com',
        description: 'Servidor de producción'
      }
    ],
    tags: [
      {
        name: 'Tokens',
        description: 'Operaciones relacionadas con JWT'
      }
    ]
  },
  apis: ['./routes/*.js', './controllers/*.js']
};

const swaggerSpec = swaggerJsdoc(options);

export const setupSwagger = (app) => {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'API JWT - Documentación'
  }));
  
  // Endpoint para obtener el spec en JSON
  app.get('/api-docs.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(swaggerSpec);
  });

  console.log('Documentación Swagger disponible en: http://localhost:5000/api-docs');
};

export default swaggerSpec;