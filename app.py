# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from controllers.pagos_controller import pagos_bp
import logging

# ----------------------------------------
# Configuración global de la app
# ----------------------------------------
app = Flask(__name__)
CORS(app)  # Habilitar CORS para llamadas desde el frontend

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Registro de blueprints (rutas externas)
app.register_blueprint(pagos_bp, url_prefix="/api")


# ----------------------------------------
# Ruta principal (Home / Health)
# ----------------------------------------
@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "mensaje": "API de Pagos funcionando 🚀",
        "version": "1.0.0"
    }), 200


# ----------------------------------------
# Punto de arranque
# ----------------------------------------
if __name__ == "__main__":
    logging.info("🚀 Iniciando servidor...")
    logging.info("📍 URL: http://localhost:5000")
    logging.info("➡️  Rutas disponibles:")
    logging.info("   GET  /")
    logging.info("   GET  /api/health")
    logging.info("   GET  /api/pagos")
    logging.info("   POST /api/pagos")
    logging.info("   POST /api/pagos/<id>/procesar")
    logging.info("   GET  /api/pagos/<id>")
    logging.info("   GET  /api/pagos/orden/<orden_id>")
    logging.info("   GET  /api/facturas")
    logging.info("   POST /api/facturas")
    logging.info("   GET  /api/facturas/<numero>")
    logging.info("   POST /api/pagos/completo")

    app.run(debug=True, port=5000, host='0.0.0.0')