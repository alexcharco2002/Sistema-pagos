from flask import Blueprint, request, jsonify
from datetime import datetime
import sqlite3, json

# =========================
#   BASE DE DATOS
# =========================

class Database:
    def __init__(self, db_name='pagos.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orden_id TEXT NOT NULL UNIQUE,
                usuario_id INTEGER NOT NULL,
                monto_total REAL NOT NULL,
                metodo_pago TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                fecha_actualizacion TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT NOT NULL UNIQUE,
                pago_id INTEGER NOT NULL,
                orden_id TEXT NOT NULL,
                usuario_id INTEGER NOT NULL,
                monto_total REAL NOT NULL,
                impuesto REAL NOT NULL,
                subtotal REAL NOT NULL,
                items TEXT NOT NULL,
                fecha_emision TEXT NOT NULL,
                FOREIGN KEY (pago_id) REFERENCES pagos (id)
            )
        ''')
        
        conn.commit()
        conn.close()


# =========================
#   MODELOS
# =========================

class Pago:
    def __init__(self, db):
        self.db = db
    
    def crear_pago(self, orden_id, usuario_id, monto_total, metodo_pago):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        fecha = datetime.now().isoformat()

        try:
            cursor.execute("""
                INSERT INTO pagos (orden_id, usuario_id, monto_total, metodo_pago, estado, fecha_creacion, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (orden_id, usuario_id, monto_total, metodo_pago, "pendiente", fecha, fecha))

            conn.commit()
            pago_id = cursor.lastrowid
            conn.close()

            return {
                "id": pago_id,
                "orden_id": orden_id,
                "usuario_id": usuario_id,
                "monto_total": monto_total,
                "metodo_pago": metodo_pago,
                "estado": "pendiente",
                "fecha_creacion": fecha
            }
        except sqlite3.IntegrityError:
            conn.close()
            return None


    def procesar_pago(self, pago_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pagos WHERE id = ?", (pago_id,))
        pago = cursor.fetchone()

        if not pago:
            conn.close()
            return {"success": False, "mensaje": "Pago no encontrado"}

        import random
        codigo = f"TXN-{random.randint(100000,999999)}"
        fecha = datetime.now().isoformat()

        cursor.execute("UPDATE pagos SET estado='aprobado', fecha_actualizacion=? WHERE id=?", (fecha, pago_id))

        cursor.execute("""
            INSERT INTO transacciones (pago_id, codigo_transaccion, estado, mensaje, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (pago_id, codigo, "aprobado", "Pago procesado", fecha))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "pago_id": pago_id,
            "codigo_transaccion": codigo,
            "mensaje": "Pago procesado"
        }


    def obtener_pago(self, pago_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pagos WHERE id=?", (pago_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "orden_id": row[1],
                "usuario_id": row[2],
                "monto_total": row[3],
                "metodo_pago": row[4],
                "estado": row[5],
                "fecha_creacion": row[6],
                "fecha_actualizacion": row[7]
            }
        return None


    def obtener_pago_por_orden(self, orden_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pagos WHERE orden_id=?", (orden_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "orden_id": row[1],
                "usuario_id": row[2],
                "monto_total": row[3],
                "metodo_pago": row[4],
                "estado": row[5],
                "fecha_creacion": row[6],
                "fecha_actualizacion": row[7]
            }
        return None



class Factura:
    def __init__(self, db):
        self.db = db

    def generar_factura(self, pago_id, items, tasa=0.12):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pagos WHERE id=? AND estado='aprobado'", (pago_id,))
        pago = cursor.fetchone()

        if not pago:
            conn.close()
            return {"success": False, "mensaje": "Pago no aprobado"}

        subtotal = pago[3] / (1 + tasa)
        impuesto = pago[3] - subtotal

        import random
        factura_num = f"FAC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
        fecha = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO facturas (numero_factura, pago_id, orden_id, usuario_id, monto_total, impuesto, subtotal, items, fecha_emision)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (factura_num, pago_id, pago[1], pago[2], pago[3], impuesto, subtotal, json.dumps(items), fecha))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "numero_factura": factura_num,
            "pago_id": pago_id,
            "items": items
        }



# =====================================================
# BLUEPRINTS (RUTAS)
# =====================================================

db = Database()
pago_model = Pago(db)
factura_model = Factura(db)

health_bp = Blueprint("health", __name__)
pagos_bp = Blueprint("pagos", __name__)
facturas_bp = Blueprint("facturas", __name__)

# ---- HEALTH ----
@health_bp.route("/api/health")
def health():
    return jsonify({"status": "ok"})


# ---- PAGOS ----
@pagos_bp.post("/api/pagos")
def crear_pago_route():
    data = request.get_json()
    pago = pago_model.crear_pago(data["orden_id"], data["usuario_id"], data["monto_total"], data["metodo_pago"])
    if pago:
        return jsonify(pago), 201
    return jsonify({"error": "Pago ya existe"}), 409


@pagos_bp.post("/api/pagos/<int:pago_id>/procesar")
def procesar_pago_route(pago_id):
    return jsonify(pago_model.procesar_pago(pago_id))


@pagos_bp.get("/api/pagos/<int:pago_id>")
def obtener_pago_route(pago_id):
    pago = pago_model.obtener_pago(pago_id)
    if pago:
        return jsonify(pago)
    return jsonify({"error": "No encontrado"}), 404


@pagos_bp.get("/api/pagos/orden/<orden_id>")
def obtener_por_orden_route(orden_id):
    pago = pago_model.obtener_pago_por_orden(orden_id)
    if pago:
        return jsonify(pago)
    return jsonify({"error": "No encontrado"}), 404


# ---- FACTURAS ----
@facturas_bp.post("/api/facturas")
def generar_factura_route():
    data = request.get_json()
    factura = factura_model.generar_factura(data["pago_id"], data["items"])
    return jsonify(factura)
    

@facturas_bp.get("/api/facturas/<numero>")
def obtener_factura_route(numero):
    factura = factura_model.obtener_factura(numero)
    if factura:
        return jsonify(factura)
    return jsonify({"error": "No encontrada"}), 404
