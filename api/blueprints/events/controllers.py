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
    return get_by_id("events", event_id)

