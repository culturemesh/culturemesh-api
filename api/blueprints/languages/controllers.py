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

@languages.route("/language/autocomplete", methods=["GET"])
@require_apikey
def get_language_autocomplete():
    input_text = request.args['input_text']

    connection = mysql.get_db()
    cursor = connection.cursor()

    # TODO: this is entirely unsafe, need better way to
    #       work with autocomplete.
    query = "SELECT * \
             FROM languages \
             WHERE name REGEXP %s \
             ORDER BY num_speakers DESC \
             LIMIT 20" % input_text

    cursor.execute(query)
    langs = cursor.fetchall()
    if len(langs) == 0:
      cursor.close()
      return make_response(jsonify([]), HTTPStatus.OK)

    langs = convert_objects(langs, cursor.description)
    cursor.close()
    return make_response(jsonify(langs), HTTPStatus.OK)
