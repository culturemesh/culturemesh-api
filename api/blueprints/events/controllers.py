from flask import Blueprint, request, g
from api import require_apikey

from api.blueprints.accounts.controllers import auth
from api.blueprints.users.utils import _add_user_to_event
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
@auth.login_required
@require_apikey
def make_new_event():
    req_obj = make_fake_request_obj(request)
    req_obj.form["id_host"] = g.user.id
    if request.method == 'POST':
        # POST
        content_fields = ['id_network', 'id_host', \
                'event_date', 'title', \
                'address_1', 'address_2', \
                'country', 'city', \
                'region', 'description']
        response = execute_post_by_table(request, content_fields, "events")
        # Unfortunately, we have to get the event id
        content = request.get_json()
        if not content:
            content = request.form
        connection = mysql.get_db()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM events WHERE id_host=%s AND id_network=%s ORDER BY id DESC LIMIT 1",
                       (content["id_host"], content["id_network"]))
        obj = cursor.fetchone()
        event_id = convert_objects([obj], cursor.description)[0]["id"]
        # We also need to "register" them attending their own event.
        _add_user_to_event(content["id_host"], event_id, "host")
        return response
    else:
        # PUT
        # Check if user is authorized to update this event
        event = get_by_id("events", request.form["id"], [])
        if event and "id_user" in event and event["id_user"] == g.user.id:
            return execute_put_by_id(req_obj, "events")


@events.route("/currentUserEventsByNetwork/<network_id>", methods=["GET"])
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

@events.route("/delete", methods=["DELETE"])
@require_apikey
@auth.login_required
def delete_event():
    event_id = request.args.get('id')
    if not event_id or not event_id.isdigit():
      return make_response("Invalid Input", HTTPStatus.BAD_REQUEST)

    connection = mysql.get_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM event_registration WHERE id_event=%s", (event_id))
    cursor.execute("DELETE FROM events WHERE id=%s", (event_id))
    cursor.close()
    connection.commit()
    return make_response("OK", HTTPStatus.OK)
