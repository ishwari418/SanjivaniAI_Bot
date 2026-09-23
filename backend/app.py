from flask import Flask
from flask_cors import CORS

from models.database import init_db
from routes.chat import chat_bp
from routes.documents import documents_bp
from routes.health import health_bp


def create_app():
    app = Flask(__name__)
    CORS(app)  # dev-friendly default; tighten origins for production

    init_db()

    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(documents_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
