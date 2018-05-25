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
    # TODO: Since we can't let pymysql put quotes for us (we need the %'s in between to have regex), we have to do
    # a direct format. This is a SQL injection vulnerability.
    # First, get relevant cities.

    conn = mysql.get_db()
    location_objects = []
    city_cur = conn.cursor()
    city_cur.execute("SELECT cities.name, id AS city_id, region_id, country_id FROM cities WHERE cities.name REGEXP %s LIMIT 100"
                     , (request.args["input_text"],))
    location_objects.extend(convert_objects(city_cur.fetchall(), city_cur.description))
    if len(location_objects) == 100:  # If we already have 100 results, which is plenty, let's just return those.
        return make_response(jsonify(location_objects), HTTPStatus.OK)
    region_cur = conn.cursor()
    region_cur.execute("SELECT regions.name, 'null' AS city_id, id AS region_id, country_id FROM regions WHERE regions.name REGEXP %s LIMIT 100"
                       , (request.args["input_text"],))
    location_objects.extend(convert_objects(region_cur.fetchall(), region_cur.description))
    if len(location_objects) == 100:
        return make_response(jsonify(location_objects), HTTPStatus.OK)
    country_cur = conn.cursor()
    country_cur.execute("SELECT countries.name, 'null' AS city_id, 'null' AS region_id, id AS country_id FROM countries WHERE countries.name REGEXP %s LIMIT 100"
                        , (request.args["input_text"],))
    location_objects.extend(convert_objects(country_cur.fetchall(), country_cur.description))
    return make_response(jsonify(location_objects), HTTPStatus.OK)



