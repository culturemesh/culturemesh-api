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

@networks.route("/<network_id>/events", methods=["GET"])
@require_apikey
def get_network_events(network_id):
    conn = mysql.get_db()
    count = int(request.args.get("count", 100))
    cursor = conn.cursor()
    query = "SELECT * \
             FROM events \
             WHERE id_network=%s"
    order = "ORDER BY id DESC"
    if "max_id" in request.args:
      max_id = request.args["max_id"]
      query += " AND id <= %s"
      cursor.execute(query + order, (network_id, max_id))
    else:
      cursor.execute(query + order, (network_id,))
    events = cursor.fetchmany(count)

    if len(events) == 0:
      return make_response(jsonify([]), HTTPStatus.OK)

    events = convert_objects(events, cursor.description)
    cursor.close()
    return make_response(jsonify(events), HTTPStatus.OK)

@networks.route("/<network_id>/users", methods=["GET"])
@require_apikey
def get_network_users(network_id):
    conn = mysql.get_db()
    count = int(request.args.get("count", 100))
    users_cursor = conn.cursor()
    query = "SELECT users.*, join_date \
             FROM network_registration \
             INNER JOIN users \
             ON users.id = network_registration.id_user \
             WHERE id_network=%s"
    order = "ORDER BY join_date DESC"
    if "max_registration_date" in request.args:
      max_registration_date = request.args["max_registration_date"]
      query += " AND join_date <= %s"
      users_cursor.execute(query + order, (network_id, max_registration_date))
    else:
      users_cursor.execute(query + order, (network_id,))
    users = users_cursor.fetchmany(count)

    if len(users) == 0:
      return make_response(jsonify([]), HTTPStatus.OK)

    users = convert_objects(users, users_cursor.description)
    users_cursor.close()
    return make_response(jsonify(users), HTTPStatus.OK)
