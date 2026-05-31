from flask import Flask, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Backend funcionando"})

    return app
