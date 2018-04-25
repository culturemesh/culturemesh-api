from flask import Blueprint, current_app
from api import require_apikey
from api.extensions import mysql
from flask import jsonify

users = Blueprint('user', __name__)


@users.route("/ping")
@require_apikey
def test():
    return "pong"


"""
Queries users according to filter.
"""


@users.route("/users")
@require_apikey
def users_query():
    cursor = mysql.get_db().cursor()
    cursor.execute("SELECT email FROM users WHERE id=2")
    return jsonify( cursor.fetchone())
