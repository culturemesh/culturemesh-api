from flask import Blueprint, jsonify, request, json, make_response
from api import require_apikey
from api.extensions import mysql
from json.decoder import JSONDecodeError
users = Blueprint('user', __name__)


@users.route("/ping")
@require_apikey
def test():
    return "pong"


"""
Queries users according to filter.
"""


@users.route("/users")
@require_apikey
def users_query():
    # Allegedly, we need to run get_data() first
    request.get_data()
    try:
        request_filter = json.loads(request.data)
    except JSONDecodeError:
        return make_response("Error: malformed request body", 400)

    connection = mysql.get_db()
    network_ids = []
    for near_loc in request_filter['near_location']:
        near_query_string = "id_city_cur=%d AND id_region_cur=%d AND id_city_cur=%d", (near_loc.city_id,
                                                                                       near_loc.region_id,
                                                                                       near_loc.country_id)
        for from_loc in request_filter['from_location']:
            # Query networks with that near and from_location
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id FROM networks WHERE %s AND id_city_origin=%d AND id_region_origin=%d AND id_country_origin=%d",
                (near_query_string, from_loc.city_id, from_loc.region_id, from_loc.country_id))
            network_ids.append(cursor.fetchall())
            cursor.commit()
            cursor.close()

        for lang in request_filter['language']:
            # Query networks with that near location and language
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM networks WHERE %s AND language_origin=%s", (near_query_string, lang))
            network_ids.append(cursor.fetchall())
            cursor.commit()
            cursor.close()
    # Now we need to get all the users subscribed to these networks.
    user_id_cursor = connection.cursor()
    user_id_cursor.execute("SELECT id_user FROM network_registration WHERE id_network IN %s", (tuple(network_ids),))
    user_ids = user_id_cursor.fetchall()
    users_cursor = connection.cursor()
    users_cursor.execute("SELECT * FROM users WHERE id IN %s", (tuple(user_ids),))
    users_res = users_cursor.fetchall()
    connection.close()
    return jsonify(users_res)
