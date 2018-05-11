from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

events = Blueprint('event', __name__)

@events.route("/ping")
@require_apikey
def test():
    return "pong"

@events.route("/<event_id>", methods=["GET"])
@require_apikey
def get_event(event_id):
    connection = mysql.get_db()
    events_cursor = connection.cursor()

    events_cursor.execute('SELECT * '
                         'FROM events '
                         'WHERE id=%s', (event_id,))

    response = make_response_from_single_tuple(events_cursor)
    events_cursor.close()
    return response

