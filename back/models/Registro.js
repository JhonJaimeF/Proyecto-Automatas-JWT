import mongoose from "mongoose";
import AutoIncrementFactory from "mongoose-sequence";

const AutoIncrement = AutoIncrementFactory(mongoose);

const RegistroSchema = new mongoose.Schema(
  {
    estado: {
      type: String,
      enum: ["valido", "invalido", "Corrupto"],
      required: true
    },
    descripcion: {
      type: Object,
      required: true
    }
  },
  {
    timestamps: { createdAt: "fecha_creacion", updatedAt: false }
  }
);

// Aplicar el plugin con la opción disable_hooks
RegistroSchema.plugin(AutoIncrement, { 
  inc_field: "id_incremental",
  disable_hooks: true
});

export default mongoose.model("Registro", RegistroSchema);