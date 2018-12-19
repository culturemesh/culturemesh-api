from flask import Blueprint, request
from api import require_apikey
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
    # TODO: Have fancier queries. For now, we will just take advantage of regex, which functions as a "contains"
    # a direct format. This is a SQL injection vulnerability.
    location_objects = []

    sql_q_format = "SELECT cities.name, id AS city_id, region_id, country_id " \
                   "FROM cities WHERE cities.name REGEXP %s"
    items, descr = execute_get_many(sql_q_format,
                                    (request.args["input_text"],), 100)

    location_objects.extend(convert_objects(items, descr))
    if len(location_objects) == 100:
        return make_response(jsonify(location_objects), HTTPStatus.OK)

    sql_q_format = "SELECT regions.name, 'null' AS city_id, id AS region_id, " \
                   "country_id FROM regions WHERE regions.name REGEXP %s"
    items, descr = execute_get_many(sql_q_format,
                                    (request.args["input_text"],), 100)

    location_objects.extend(convert_objects(items, descr))
    if len(location_objects) == 100:
        return make_response(jsonify(location_objects), HTTPStatus.OK)

    sql_q_format = "SELECT countries.name, 'null' AS city_id, 'null' AS " \
                   "region_id, id AS country_id FROM countries WHERE " \
                   "countries.name REGEXP %s"
    items, descr = execute_get_many(sql_q_format,
                                    (request.args["input_text"],), 100)

    location_objects.extend(convert_objects(items, descr))
    return make_response(jsonify(location_objects), HTTPStatus.OK)
