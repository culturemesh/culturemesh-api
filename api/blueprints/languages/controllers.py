from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

languages = Blueprint('language', __name__)


@languages.route("/ping")
@require_apikey
def test():
    return "pong"

@languages.route("/<lang_id>", methods=["GET"])
@require_apikey
def get_language(lang_id):
    return get_by_id("languages", lang_id)
