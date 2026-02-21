# backend/src/logging_config.py

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask
from src.config import SENTRY_DSN, FLASK_ENV


def init_logging(app: Flask) -> None:
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=FLASK_ENV,
        )
        app.logger.info("🤖 Sentry initialized")
