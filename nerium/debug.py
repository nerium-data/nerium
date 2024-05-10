from flask import Flask

app = Flask(__name__)


class DebugModeChecker:

    @staticmethod
    def is_debug_mode():
        return app.debug
