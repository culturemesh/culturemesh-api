from flask import Blueprint, jsonify, request, json, make_response
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

languages = Blueprint('language', __name__)


@languages.route("/ping")
def test():
    return "pong"


@languages.route("/<lang_id>", methods=["GET"])
def get_language(lang_id):
    return get_by_id("languages", lang_id)


@languages.route("/autocomplete", methods=["GET"])
def get_language_autocomplete():
    input_text = request.args['input_text']
    if input_text is None:
        return make_response("Must have valid input_text field",
                             HTTPStatus.METHOD_NOT_ALLOWED)

    # TODO: this is entirely unsafe, need better way to
    #       work with autocomplete.
    query = "SELECT * FROM languages WHERE languages.name REGEXP %s " \
            "ORDER BY num_speakers DESC;"
    items, descr = execute_get_many(query, (input_text,), 20)
    if len(items) == 0:
        return make_response(jsonify([]), HTTPStatus.OK)

    langs = convert_objects(items, descr)
    return make_response(jsonify(langs), HTTPStatus.OK)
