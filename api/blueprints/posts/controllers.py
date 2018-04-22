from flask import Blueprint
from api import require_apikey

posts = Blueprint('post', __name__)

@posts.route("/ping")
@require_apikey
def test():
    return "pong"
