from flask import Blueprint
from api import require_apikey

accounts = Blueprint('account', __name__)

@accounts.route("/ping")
@require_apikey
def test():
    return "pong"
