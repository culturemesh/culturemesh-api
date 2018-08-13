from flask import Blueprint, request, g
from api import require_apikey

from api.blueprints.accounts.controllers import auth
from api.blueprints.users.utils import add_user_to_event
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
        response = execute_post_by_table(request, content_fields, "events")
        # We also need to "register" them attending their own event.
        if response.status == 200:
            add_user_to_event(request.args["id_host"], response.get_json()["id"], "host")
        return response
    else:
        # PUT
        return execute_put_by_id(request, "events")


@events.route("/userEventsForNetwork/<network_id>", methods=["GET"])
@require_apikey
@auth.login_required
def user_events_for_network(network_id):
    user_id = g.user.id
    return get_paginated("SELECT * \
                         FROM event_registration INNER JOIN events ON events.id = event_registration.id_event \
                         WHERE (id_guest=%s OR id_host=%s) AND id_network=%s",
                         selection_fields=[user_id, user_id, network_id],
                         args= request.args,
                         order_clause="ORDER BY id DESC",
                         order_index_format="id <= %s",
                         order_arg="id")