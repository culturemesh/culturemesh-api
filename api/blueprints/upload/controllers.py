from flask import Blueprint
from api import require_apikey


upload = Blueprint('upload', __name__)


@upload.route("/ping")
@require_apikey
def test():
    return "pong"
