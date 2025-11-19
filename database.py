import sqlite3
from datetime import datetime
import json

class Database:
    def __init__(self, db_name='pagos.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Inicializa las tablas de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de pagos
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
        
        # Tabla de facturas
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
        
        # Tabla de transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pago_id INTEGER NOT NULL,
                codigo_transaccion TEXT NOT NULL UNIQUE,
                estado TEXT NOT NULL,
                mensaje TEXT,
                fecha TEXT NOT NULL,
                FOREIGN KEY (pago_id) REFERENCES pagos (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")


class Pago:
    def __init__(self, db):
        self.db = db
    
    def crear_pago(self, orden_id, usuario_id, monto_total, metodo_pago):
        """Crea un nuevo registro de pago"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        fecha_actual = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO pagos (orden_id, usuario_id, monto_total, metodo_pago, estado, fecha_creacion, fecha_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (orden_id, usuario_id, monto_total, metodo_pago, 'pendiente', fecha_actual, fecha_actual))
            
            pago_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'id': pago_id,
                'orden_id': orden_id,
                'usuario_id': usuario_id,
                'monto_total': monto_total,
                'metodo_pago': metodo_pago,
                'estado': 'pendiente',
                'fecha_creacion': fecha_actual
            }
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def procesar_pago(self, pago_id):
        """Simula el procesamiento de un pago"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Obtener información del pago
        cursor.execute('SELECT * FROM pagos WHERE id = ?', (pago_id,))
        pago = cursor.fetchone()
        
        if not pago:
            conn.close()
            return {'success': False, 'mensaje': 'Pago no encontrado'}
        
        # Simular procesamiento (siempre exitoso para esta demo)
        import random
        codigo_transaccion = f"TXN-{random.randint(100000, 999999)}"
        estado = 'aprobado'  # Podría ser 'rechazado' en casos reales
        
        fecha_actual = datetime.now().isoformat()
        
        # Actualizar estado del pago
        cursor.execute('''
            UPDATE pagos 
            SET estado = ?, fecha_actualizacion = ?
            WHERE id = ?
        ''', (estado, fecha_actual, pago_id))
        
        # Registrar transacción
        cursor.execute('''
            INSERT INTO transacciones (pago_id, codigo_transaccion, estado, mensaje, fecha)
            VALUES (?, ?, ?, ?, ?)
        ''', (pago_id, codigo_transaccion, estado, 'Pago procesado exitosamente', fecha_actual))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'pago_id': pago_id,
            'codigo_transaccion': codigo_transaccion,
            'estado': estado,
            'mensaje': 'Pago procesado exitosamente'
        }
    
    def obtener_pago(self, pago_id):
        """Obtiene información de un pago"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pagos WHERE id = ?', (pago_id,))
        pago = cursor.fetchone()
        conn.close()
        
        if pago:
            return {
                'id': pago[0],
                'orden_id': pago[1],
                'usuario_id': pago[2],
                'monto_total': pago[3],
                'metodo_pago': pago[4],
                'estado': pago[5],
                'fecha_creacion': pago[6],
                'fecha_actualizacion': pago[7]
            }
        return None


class Factura:
    def __init__(self, db):
        self.db = db
    
    def generar_factura(self, pago_id, items, tasa_impuesto=0.12):
        """Genera una factura para un pago aprobado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Verificar que el pago existe y está aprobado
        cursor.execute('SELECT * FROM pagos WHERE id = ? AND estado = ?', (pago_id, 'aprobado'))
        pago = cursor.fetchone()
        
        if not pago:
            conn.close()
            return {'success': False, 'mensaje': 'Pago no encontrado o no aprobado'}
        
        # Calcular montos
        subtotal = pago[3] / (1 + tasa_impuesto)
        impuesto = pago[3] - subtotal
        
        # Generar número de factura
        import random
        numero_factura = f"FAC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        fecha_emision = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO facturas (numero_factura, pago_id, orden_id, usuario_id, monto_total, impuesto, subtotal, items, fecha_emision)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (numero_factura, pago_id, pago[1], pago[2], pago[3], impuesto, subtotal, json.dumps(items), fecha_emision))
            
            factura_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'id': factura_id,
                'numero_factura': numero_factura,
                'pago_id': pago_id,
                'orden_id': pago[1],
                'usuario_id': pago[2],
                'subtotal': round(subtotal, 2),
                'impuesto': round(impuesto, 2),
                'monto_total': pago[3],
                'items': items,
                'fecha_emision': fecha_emision
            }
        except sqlite3.IntegrityError:
            conn.close()
            return {'success': False, 'mensaje': 'La factura ya existe para este pago'}
    
    def obtener_factura(self, numero_factura):
        """Obtiene una factura por su número"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM facturas WHERE numero_factura = ?', (numero_factura,))
        factura = cursor.fetchone()
        conn.close()
        
        if factura:
            return {
                'id': factura[0],
                'numero_factura': factura[1],
                'pago_id': factura[2],
                'orden_id': factura[3],
                'usuario_id': factura[4],
                'monto_total': factura[5],
                'impuesto': factura[6],
                'subtotal': factura[7],
                'items': json.loads(factura[8]),
                'fecha_emision': factura[9]
            }
        return None


# Ejemplo de uso
if __name__ == '__main__':
    # Inicializar base de datos
    db = Database()
    
    # Crear instancias de modelos
    pago_model = Pago(db)
    factura_model = Factura(db)
    
    # Ejemplo: Crear un pago
    print("\n📝 Creando pago...")
    nuevo_pago = pago_model.crear_pago(
        orden_id='ORD-001',
        usuario_id=123,
        monto_total=112.00,
        metodo_pago='tarjeta_credito'
    )
    print(f"✅ Pago creado: {nuevo_pago}")
    
    # Ejemplo: Procesar el pago
    print("\n💳 Procesando pago...")
    resultado = pago_model.procesar_pago(nuevo_pago['id'])
    print(f"✅ Resultado: {resultado}")
    
    # Ejemplo: Generar factura
    print("\n🧾 Generando factura...")
    items = [
        {'nombre': 'Producto A', 'cantidad': 2, 'precio': 25.00},
        {'nombre': 'Producto B', 'cantidad': 1, 'precio': 62.00}
    ]
    factura = factura_model.generar_factura(nuevo_pago['id'], items)
    print(f"✅ Factura generada: {factura}")