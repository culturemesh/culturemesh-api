from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

locations = Blueprint('location', __name__)


@locations.route("/ping")
@require_apikey
def test():
    return "pong"


@locations.route("/countries/<country_id>", methods=["GET"])
@require_apikey
def get_country(country_id):
    return get_by_id("countries", country_id)


@locations.route("/regions/<region_id>", methods=["GET"])
@require_apikey
def get_region(region_id):
    return get_by_id("regions", region_id)


@locations.route("/cities/<city_id>", methods=["GET"])
@require_apikey
def get_city(city_id):
    return get_by_id("cities", city_id)


@locations.route("/autocomplete", methods=["GET"])
@require_apikey
def autocomplete():
    # TODO: Have fancier queries. For now, we will just take advantage of regex.
    # First, get relevant cities.
    conn = mysql.get_db()
    location_objects = []
    city_cur = conn.cursor()
    city_cur.execute("SELECT id AS city_id, region_id, country_id FROM cities WHERE cities.name LIKE '%%' + %s + '%%' LIMIT 100",
                     request.args["input_text"])
    location_objects.extend(city_cur.fetchall())
    city_cur.close()
    if len(location_objects) == 100:
        return make_response(jsonify(convert_objects(location_objects)), HTTPStatus.OK)
    # location_objects.extend("SELECT id AS region_id, country_id FROM regions WHERE regions.name LIKE ")]
    return make_response(jsonify(location_objects), HTTPStatus.OK)
