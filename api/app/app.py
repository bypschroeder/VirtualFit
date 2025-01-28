from flask import Flask
from services.s3 import s3, create_buckets
from services.init_data import upload_data
from routes import main
from logger import setup_logger
from config import Config


def create_app():
    app = Flask(__name__)  # Flask app
    app.config.from_object(Config)  # Load config

    create_buckets(app.config["BUCKETS"], app)  # Create bucketsj
    upload_data(
        s3, app.config["BUCKETS"][1], "./init_data/models", app
    )  # Upload init data

    setup_logger(app)  # Setup logger

    app.register_blueprint(main)  # Register blueprint

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=3000, debug=True)
