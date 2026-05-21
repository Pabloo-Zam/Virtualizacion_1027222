from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os
import re

app = Flask(__name__)
CORS(app)

mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_host = os.getenv("MONGO_HOST")
mongo_database = os.getenv("MONGO_DATABASE")

mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:27017/"

client = MongoClient(mongo_uri)
db = client[mongo_database]
inscripciones = db["inscripciones"]


def correo_valido(correo):
    patron = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return re.match(patron, correo) is not None


def convertir_inscripcion(item):
    return {
        "id": str(item["_id"]),
        "nombre": item.get("nombre"),
        "correo": item.get("correo"),
        "telefono": item.get("telefono"),
        "sede": item.get("sede"),
        "plan": item.get("plan"),
        "fecha_inscripcion": item.get("fecha_inscripcion").strftime("%Y-%m-%d %H:%M:%S")
        if item.get("fecha_inscripcion") else None
    }


def validar_datos(data):
    campos_obligatorios = ["nombre", "correo", "telefono", "sede", "plan"]

    if not data:
        return "No se recibieron datos"

    for campo in campos_obligatorios:
        if campo not in data or not str(data[campo]).strip():
            return f"El campo {campo} es obligatorio"

    if not correo_valido(data["correo"].strip().lower()):
        return "El correo ingresado no tiene un formato válido"

    if len(data["telefono"].strip()) < 8:
        return "El teléfono debe tener al menos 8 dígitos"

    return None


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "mensaje": "Backend Flask del gimnasio funcionando correctamente"
    })


@app.route("/api/health", methods=["GET"])
def health():
    try:
        client.admin.command("ping")
        return jsonify({
            "frontend": "Frontend conectado con Backend",
            "backend": "Backend Flask funcionando",
            "mongodb": "MongoDB conectado correctamente"
        }), 200
    except Exception as error:
        return jsonify({
            "backend": "Backend funcionando",
            "mongodb": "Error al conectar con MongoDB",
            "detalle": str(error)
        }), 500


@app.route("/api/inscripciones", methods=["GET"])
def obtener_inscripciones():
    registros = []

    for item in inscripciones.find().sort("fecha_inscripcion", -1):
        registros.append(convertir_inscripcion(item))

    return jsonify(registros), 200


@app.route("/api/inscripciones", methods=["POST"])
def crear_inscripcion():
    data = request.get_json()

    error = validar_datos(data)
    if error:
        return jsonify({"error": error}), 400

    nueva_inscripcion = {
        "nombre": data["nombre"].strip(),
        "correo": data["correo"].strip().lower(),
        "telefono": data["telefono"].strip(),
        "sede": data["sede"].strip(),
        "plan": data["plan"].strip(),
        "fecha_inscripcion": datetime.now()
    }

    try:
        resultado = inscripciones.insert_one(nueva_inscripcion)
        nueva_inscripcion["_id"] = resultado.inserted_id

        return jsonify({
            "mensaje": "Inscripción registrada correctamente",
            "inscripcion": convertir_inscripcion(nueva_inscripcion)
        }), 201

    except DuplicateKeyError:
        return jsonify({
            "error": "Ya existe una inscripción con ese correo o teléfono"
        }), 409

    except Exception as error:
        return jsonify({
            "error": "Error interno al guardar la inscripción",
            "detalle": str(error)
        }), 500


@app.route("/api/inscripciones/<id>", methods=["PUT"])
def actualizar_inscripcion(id):
    data = request.get_json()

    error = validar_datos(data)
    if error:
        return jsonify({"error": error}), 400

    try:
        object_id = ObjectId(id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400

    datos_actualizados = {
        "nombre": data["nombre"].strip(),
        "correo": data["correo"].strip().lower(),
        "telefono": data["telefono"].strip(),
        "sede": data["sede"].strip(),
        "plan": data["plan"].strip(),
        "fecha_actualizacion": datetime.now()
    }

    try:
        resultado = inscripciones.update_one(
            {"_id": object_id},
            {"$set": datos_actualizados}
        )

        if resultado.matched_count == 0:
            return jsonify({
                "error": "No se encontró la inscripción"
            }), 404

        registro_actualizado = inscripciones.find_one({"_id": object_id})

        return jsonify({
            "mensaje": "Inscripción actualizada correctamente",
            "inscripcion": convertir_inscripcion(registro_actualizado)
        }), 200

    except DuplicateKeyError:
        return jsonify({
            "error": "Ya existe otra inscripción con ese correo o teléfono"
        }), 409

    except Exception as error:
        return jsonify({
            "error": "Error interno al actualizar la inscripción",
            "detalle": str(error)
        }), 500


@app.route("/api/inscripciones/<id>", methods=["DELETE"])
def eliminar_inscripcion(id):
    try:
        object_id = ObjectId(id)
    except InvalidId:
        return jsonify({"error": "ID inválido"}), 400

    resultado = inscripciones.delete_one({"_id": object_id})

    if resultado.deleted_count == 0:
        return jsonify({
            "error": "No se encontró la inscripción"
        }), 404

    return jsonify({
        "mensaje": "Inscripción eliminada correctamente"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)