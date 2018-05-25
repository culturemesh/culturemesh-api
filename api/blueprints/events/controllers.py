from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from http import HTTPStatus
from api.extensions import mysql
from api.apiutils import *

events = Blueprint('event', __name__)

@events.route("/ping")
@require_apikey
def test():
    return "pong"

@events.route("/<event_id>", methods=["GET"])
@require_apikey
def get_event(event_id):
    return get_by_id("events", event_id)

@events.route("/<event_id>/reg", methods=["GET"])
@require_apikey
def get_event_registration(event_id):
    return get_paginated("SELECT * \
                          FROM event_registration \
                          WHERE id_event=%s",
                          selection_fields=[event_id],
                          args=request.args,
                          order_clause="ORDER BY date_registered DESC",
                          order_index_format="date_registered <= %s",
                          order_arg="max_registration_date")

@events.route("/new", methods=["POST", "PUT"])
@require_apikey
def make_new_event():
    if request.method == 'POST':

      # POST
      content_fields = ['id_network', 'id_host', \
                'event_date', 'title', \
                'address_1', 'address_2', \
                'country', 'city', \
                'region', 'description']

      return execute_post_by_table(request, content_fields, "events")
    else:

      # PUT
      return execute_put_by_id(request, "events")
