from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

networks = Blueprint('network', __name__)

@networks.route("/ping")
@require_apikey
def test():
    return "pong"

@networks.route("/<network_id>", methods=["GET"])
@require_apikey
def get_network(network_id):
    connection = mysql.get_db()
    network_cursor = connection.cursor()

    network_cursor.execute('SELECT * '
                           'FROM networks '
                           'WHERE id=%s', (network_id,))

    response = make_response_from_single_tuple(network_cursor)
    network_cursor.close()
    return response
