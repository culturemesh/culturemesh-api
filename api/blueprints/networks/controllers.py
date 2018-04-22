from flask import Blueprint
from api import require_apikey

networks = Blueprint('network', __name__)

@networks.route("/ping")
@require_apikey
def test():
    return "pong"
