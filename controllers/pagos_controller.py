# controllers/pagos_controller.py
from flask import Blueprint, request, jsonify
from database.models import Database, Pago, Factura 

pagos_bp = Blueprint('pagos_bp', __name__)

# Inicializar DB y modelos (singleton por proceso)
_db = Database()
_pago_model = Pago(_db)
_factura_model = Factura(_db)


# ---------- Helpers ----------
def _bad_request(msg="Campos inválidos"):
    return jsonify({"error": msg}), 400

def _not_found(msg="No encontrado"):
    return jsonify({"error": msg}), 404


# ---------- Rutas (documentadas / listadas) ----------

@pagos_bp.get('/health')
def health():
    """GET /api/health"""
    return jsonify({"status": "ok", "servicio": "Sistema de Pagos"}), 200


@pagos_bp.post('/pagos')
def crear_pago():
    """POST /api/pagos
    Body JSON:
    {
      "orden_id": "ORD-001",
      "usuario_id": 123,
      "monto_total": 100.00,
      "metodo_pago": "tarjeta_credito"
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return _bad_request("JSON inválido")
    required = ['orden_id', 'usuario_id', 'monto_total', 'metodo_pago']
    if not all(k in data for k in required):
        return _bad_request(f"Faltan campos: {', '.join(required)}")

    pago = _pago_model.crear_pago(
        orden_id=data['orden_id'],
        usuario_id=data['usuario_id'],
        monto_total=data['monto_total'],
        metodo_pago=data['metodo_pago']
    )

    if pago is None:
        return jsonify({"error": "Ya existe un pago para esta orden"}), 409

    return jsonify(pago), 201


@pagos_bp.post('/pagos/<int:pago_id>/procesar')
def procesar_pago(pago_id: int):
    """POST /api/pagos/<id>/procesar"""
    resultado = _pago_model.procesar_pago(pago_id)
    if not resultado.get('success'):
        return _not_found(resultado.get('mensaje', 'Error procesando pago'))
    return jsonify(resultado), 200


@pagos_bp.get('/pagos/<int:pago_id>')
def obtener_pago(pago_id: int):
    """GET /api/pagos/<id>"""
    pago = _pago_model.obtener_pago(pago_id)
    if not pago:
        return _not_found("Pago no encontrado")
    return jsonify(pago), 200


@pagos_bp.get('/pagos/orden/<string:orden_id>')
def obtener_por_orden(orden_id: str):
    """GET /api/pagos/orden/<orden_id>"""
    conn = _db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pagos WHERE orden_id = ?', (orden_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return _not_found("Pago no encontrado para esta orden")
    pago = {
        'id': row[0],
        'orden_id': row[1],
        'usuario_id': row[2],
        'monto_total': row[3],
        'metodo_pago': row[4],
        'estado': row[5],
        'fecha_creacion': row[6],
        'fecha_actualizacion': row[7]
    }
    return jsonify(pago), 200


@pagos_bp.post('/facturas')
def generar_factura():
    """POST /api/facturas
    Body JSON:
    {
      "pago_id": 1,
      "items": [ { "nombre": "...", "cantidad": 1, "precio": 10.0 } ],
      "tasa_impuesto": 0.12  # opcional
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return _bad_request("JSON inválido")
    if 'pago_id' not in data or 'items' not in data:
        return _bad_request("Faltan 'pago_id' o 'items'")

    tasa = data.get('tasa_impuesto', 0.12)
    resultado = _factura_model.generar_factura(data['pago_id'], data['items'], tasa_impuesto=tasa)
    if not resultado.get('success'):
        return jsonify(resultado), 400
    return jsonify(resultado), 201


@pagos_bp.get('/facturas/<string:numero>')
def obtener_factura(numero: str):
    """GET /api/facturas/<numero>"""
    factura = _factura_model.obtener_factura(numero)
    if not factura:
        return _not_found("Factura no encontrada")
    return jsonify(factura), 200


@pagos_bp.post('/pagos/completo')
def flujo_completo():
    """POST /api/pagos/completo
    Body JSON:
    {
      "orden_id": "...",
      "usuario_id": 123,
      "monto_total": 100,
      "metodo_pago": "tarjeta",
      "items": [...]
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return _bad_request("JSON inválido")
    required = ['orden_id', 'usuario_id', 'monto_total', 'metodo_pago']
    if not all(k in data for k in required):
        return _bad_request(f"Faltan campos: {', '.join(required)}")

    # 1) Crear pago
    pago = _pago_model.crear_pago(
        orden_id=data['orden_id'],
        usuario_id=data['usuario_id'],
        monto_total=data['monto_total'],
        metodo_pago=data['metodo_pago']
    )
    if pago is None:
        return jsonify({"error": "Ya existe un pago para esta orden"}), 409

    # 2) Procesar pago
    resultado = _pago_model.procesar_pago(pago['id'])
    if not resultado.get('success'):
        return jsonify({"error": "Error al procesar pago"}), 500

    # 3) Generar factura
    factura = _factura_model.generar_factura(pago['id'], data.get('items', []))
    if not factura.get('success'):
        return jsonify({"error": "Error al generar factura", "detalle": factura}), 500

    return jsonify({
        'pago': pago,
        'transaccion': resultado,
        'factura': factura
    }), 201


@pagos_bp.get('/pagos')
def listar_pagos():
    """GET /api/pagos - Lista todos los pagos"""
    conn = _db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pagos ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    conn.close()
    
    pagos = []
    for row in rows:
        pagos.append({
            'id': row[0],
            'orden_id': row[1],
            'usuario_id': row[2],
            'monto_total': row[3],
            'metodo_pago': row[4],
            'estado': row[5],
            'fecha_creacion': row[6],
            'fecha_actualizacion': row[7]
        })
    
    return jsonify(pagos), 200


@pagos_bp.get('/facturas')
def listar_facturas():
    """GET /api/facturas - Lista todas las facturas"""
    conn = _db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM facturas ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    conn.close()
    
    facturas = []
    for row in rows:
        facturas.append({
            'id': row[0],
            'numero_factura': row[1],
            'pago_id': row[2],
            'orden_id': row[3],
            'usuario_id': row[4],
            'monto_total': row[5],
            'impuesto': row[6],
            'subtotal': row[7],
            'fecha_emision': row[9]
        })
    
    return jsonify(facturas), 200