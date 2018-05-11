from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

posts = Blueprint('post', __name__)

@posts.route("/ping")
@require_apikey
def test():
    return "pong"

@posts.route("/<post_id>", methods=["GET"])
@require_apikey
def get_post(post_id):
    return get_by_id("posts", post_id)
