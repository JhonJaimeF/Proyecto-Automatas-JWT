import mongoose from 'mongoose';

// Configuración de mongoose (esto sigue siendo útil para suprimir warnings de queries)
mongoose.set('strictQuery', false);

const connectDB = async () => {
  try {   
    const conn = await mongoose.connect(process.env.MONGO_URI);
    
    console.log(`Base DB conectada`);
  } catch (error) {
    console.error('❌ Error de conexión a MongoDB:', error.message);
    process.exit(1);
  }
};

export default connectDB;