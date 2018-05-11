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
