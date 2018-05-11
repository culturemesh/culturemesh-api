from flask import Blueprint
from api import require_apikey

languages = Blueprint('language', __name__)


@languages.route("/ping")
@require_apikey
def test():
    return "pong"
