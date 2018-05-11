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
    return get_by_id("networks", network_id)

@networks.route("/<network_id>/posts", methods=["GET"])
@require_apikey
def get_network_posts(network_id):
    conn = mysql.get_db()
    count = int(request.args.get("count", 100))
    cursor = conn.cursor()
    query = "SELECT * \
             FROM posts \
             WHERE id_network=%s"
    order = "ORDER BY id DESC"
    if "max_id" in request.args:
      max_id = request.args["max_id"]
      query += " AND id <= %s"
      cursor.execute(query + order, (network_id, max_id))
    else:
      cursor.execute(query + order, (network_id,))
    posts = cursor.fetchmany(count)

    if len(posts) == 0:
      return make_response(jsonify([]), HTTPStatus.OK)

    posts = convert_objects(posts, cursor.description)
    cursor.close()
    return make_response(jsonify(posts), HTTPStatus.OK)
