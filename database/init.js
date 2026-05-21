db = db.getSiblingDB("proyecto_db");

db.createCollection("inscripciones");

db.inscripciones.createIndex(
  { correo: 1 },
  { unique: true }
);

db.inscripciones.createIndex(
  { telefono: 1 },
  { unique: true }
);

db.inscripciones.insertOne({
  nombre: "Registro de prueba",
  correo: "prueba@gym.com",
  telefono: "00000000",
  sede: "Sede Central",
  plan: "Mensual",
  fecha_inscripcion: new Date()
});