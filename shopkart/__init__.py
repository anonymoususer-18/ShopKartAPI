"""App factory: builds and wires the whole application in one place."""
import logging

from flask import Flask, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from .config import load_settings
from .exceptions import ShopKartError
from .logging_setup import setup_logging
from .repository import Repository
from .routes import api
from .services import CheckoutService

logger = logging.getLogger("shopkart.app")


def create_app(env=None, data_file=None):
    settings = load_settings(env)                  # 1. config (fails fast if wrong)
    setup_logging(settings.app.log_level)          # 2. logging

    app = Flask(__name__)
    app.json.sort_keys = False
    app.config["SETTINGS"] = settings

    repo = Repository(data_file) if data_file else Repository()   # 3. data + business logic
    app.extensions["repository"] = repo
    app.extensions["checkout_service"] = CheckoutService(settings, repo)

    app.register_blueprint(api)                    # 4. routes
    register_error_handlers(app)                   # 5. errors

    @app.get("/health")
    def health():
        return jsonify(status="UP", app=settings.app.name, environment=settings.app.environment)

    logger.info("%s started in %s mode", settings.app.name, settings.app.environment)
    return app


def register_error_handlers(app):
    @app.errorhandler(ShopKartError)
    def handle_business_error(e):
        logger.warning("%s: %s", e.error_code, e.message)
        return jsonify(error=e.error_code, message=e.message), e.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        details = [{"field": ".".join(str(x) for x in err["loc"]), "message": err["msg"]}
                   for err in e.errors()]
        return jsonify(error="validation_failed", details=details), 422

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        if isinstance(e, HTTPException):
            return jsonify(error=e.name, message=e.description), e.code
        logger.exception("Unexpected error")
        return jsonify(error="internal_error", message="Something went wrong"), 500
