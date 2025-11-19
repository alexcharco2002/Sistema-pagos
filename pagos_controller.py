# ========================================
# CONTROLADOR DE PAGOS – BLUEPRINT
# ========================================
from flask import Blueprint, jsonify, request
from datetime import datetime
import random

pagos_bp = Blueprint("pagos", __name__)

# Base de datos simulada
pagos_db = {}
facturas_db = {}


# ----------------------------------------
# Health Check
# ----------------------------------------
@pagos_bp.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "servicio": "Sistema de Pagos"
    }), 200


# ----------------------------------------
# Crear un pago
# ----------------------------------------
@pagos_bp.post("/pagos")
def crear_pago():
    data = request.get_json()

    nuevo_id = str(len(pagos_db) + 1)
    pagos_db[nuevo_id] = {
        "id": nuevo_id,
        "orden_id": data.get("orden_id"),
        "monto": data.get("monto"),
        "fecha": datetime.now().isoformat(),
        "estado": "pendiente"
    }

    return jsonify(pagos_db[nuevo_id]), 201


# ----------------------------------------
# Procesar pago (mock)
# ----------------------------------------
@pagos_bp.post("/pagos/<id>/procesar")
def procesar_pago(id):
    if id not in pagos_db:
        return jsonify({"error": "Pago no encontrado"}), 404

    pagos_db[id]["estado"] = "procesado"

    return jsonify({
        "mensaje": "Pago procesado correctamente",
        "pago": pagos_db[id]
    }), 200


# ----------------------------------------
# Obtener pago por ID
# ----------------------------------------
@pagos_bp.get("/pagos/<id>")
def obtener_pago(id):
    if id not in pagos_db:
        return jsonify({"error": "Pago no encontrado"}), 404

    return jsonify(pagos_db[id]), 200


# ----------------------------------------
# Obtener pago por ID de orden
# ----------------------------------------
@pagos_bp.get("/pagos/orden/<orden_id>")
def pago_por_orden(orden_id):
    for p in pagos_db.values():
        if p["orden_id"] == orden_id:
            return jsonify(p), 200

    return jsonify({"error": "No existe pago para esa orden"}), 404


# ----------------------------------------
# Generar factura
# ----------------------------------------
@pagos_bp.post("/facturas")
def generar_factura():
    data = request.get_json()

    numero_factura = str(random.randint(100000, 999999))

    factura = {
        "numero": numero_factura,
        "orden_id": data.get("orden_id"),
        "monto": data.get("monto"),
        "fecha": datetime.now().isoformat()
    }

    facturas_db[numero_factura] = factura

    return jsonify(factura), 201


# ----------------------------------------
# Obtener factura por número
# ----------------------------------------
@pagos_bp.get("/facturas/<numero>")
def obtener_factura(numero):
    if numero not in facturas_db:
        return jsonify({"error": "Factura no encontrada"}), 404

    return jsonify(facturas_db[numero]), 200


# ----------------------------------------
# Flujo completo de pago + factura
# ----------------------------------------
@pagos_bp.post("/pagos/completo")
def flujo_completo():
    data = request.get_json()

    orden_id = data.get("orden_id")
    monto = data.get("monto")

    # Crear pago
    pago_id = "p" + str(len(pagos_db) + 1)
    pagos_db[pago_id] = {
        "id": pago_id,
        "orden_id": orden_id,
        "monto": monto,
        "fecha": datetime.now().isoformat(),
        "estado": "pendiente"
    }

    # Procesar pago
    pagos_db[pago_id]["estado"] = "procesado"

    # Crear factura
    factura_num = str(random.randint(100000, 999999))
    factura = {
        "numero": factura_num,
        "orden_id": orden_id,
        "monto": monto,
        "fecha": datetime.now().isoformat()
    }
    facturas_db[factura_num] = factura

    return jsonify({
        "mensaje": "Flujo completado con éxito",
        "pago": pagos_db[pago_id],
        "factura": factura
    }), 200
