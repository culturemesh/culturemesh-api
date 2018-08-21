from flask import Blueprint, request, abort
from api import require_apikey
from api.apiutils import *
from pymysql.err import IntegrityError

from api.blueprints.networks.utils import get_from_location_sql_string_end, \
  get_near_location_sql_string_start

networks = Blueprint('network', __name__)


@networks.route("/ping")
@require_apikey
def test():
    return "pong"


def make_new_network_request():
    """
    This will transform a GET /networks query to a POST /new network query by
    producing a "request" object with the necessary request.args values for a
    "POST networks/new" request. Yeah, sorry it's kinda hacksy.

    :return: The updated request object. Notice this is just a dictionary,
    since the actual request object
    is an ImmutableDict.
    """

    # this makes req an arbitrary object so I can add attributes
    # (like form and get_json) to it.
    # See: https://stackoverflow.com/questions/2280334
    req = type('', (), {})()
    req.form = {}
    conn = mysql.get_db()

    near_ids = request.args['near_location'].split(',')
    singulars = ['country', 'region', 'city']
    plurals = ['countries', 'regions', 'cities']

    for singular, plural, near_id in zip(singulars, plurals, near_ids):
        req.form['id_%s_cur' % singular] = near_id
        req.form['%s_cur' % singular] = get_column_value(
          conn, 'name', 'id', plural, near_id
        )

    if "from_location" in request.args:
        # To avoid a key error in execute_post_by_table, we need to set the other params to None
        req.form['id_language_origin'] = None
        req.form['language_origin'] = None
        from_ids = request.args['from_location'].split(',')
        for singular, plural, from_id in zip(singulars, plurals, from_ids):
            req.form['id_%s_origin' % singular] = from_id
            req.form['%s_origin' % singular] = get_column_value(
              conn, 'name', 'id', plural, from_id
            )
        if near_ids[0] != -1:
            req.form['network_class'] = 'cc'
        elif near_ids[1] != -1:
            req.form['network_class'] = 'rc'
        else:
            req.form['network_class'] = 'co'
    elif "language" in request.args:
        for singular in singulars:
            req.form['id_%s_origin' % singular] = None
            req.form['%s_origin' % singular] = None
        req.form['id_language_origin'] = get_column_value(
          conn, 'id', 'name', 'languages', request.args['language']
        )
        req.form['language_origin'] = request.args['language']
        req.form['network_class'] = '_l'

    # To avoid an error, we will make a pseudo function that returns none so
    # that execute_post_by_table will use the
    # function dictionary instead.
    else:
        # This shouldn't happen: the route should handle the input params.
        abort(HTTPStatus.BAD_REQUEST)

    def get_json():
        return None
    req.get_json = get_json
    return req


def get_column_value(db_connection,
                     desired_column,
                     query_column,
                     table_name,
                     item_id):
    """
    Fetches name from DB table given id. I also use this for languages.
    :param db_connection: Database connection (use mysql.get_db())
    :param desired_column: column you want to find out
    :param query_column: column you already know that you can use to query
    :param table_name:
    :param item_id: value corresponding to query_column, -1 if supposed to be
      "null"
    :return: name of area.
    """
    if item_id == str(-1) or str(item_id).lower() == 'null' or not item_id:
        return None
    cursor = db_connection.cursor()
    cursor.execute(
      "SELECT " + desired_column + " FROM " + table_name + " WHERE " + query_column + "=%s",
      item_id
    )
    cursor.close()
    return cursor.fetchone()


@networks.route("/networks", methods=["GET"])
@require_apikey
def get_networks(func_counter=0):
    # Validate that we have valid input data (we need a near_location).
    if "near_location" not in request.args:
        return make_response(
          "No near_location specified", HTTPStatus.METHOD_NOT_ALLOWED
        )

    selection_fields = []

    # All requests will start with the same query and query for near_location.
    my_sql_string_start, near_location_ids = get_near_location_sql_string_start(
      request.args["near_location"]
    )

    selection_fields.extend(near_location_ids)
    # Need to check if querying a location or language network.
    # That changes our queries.
    if "from_location" in request.args:
        my_sql_string_end, from_location_ids = get_from_location_sql_string_end(
           request.args["from_location"]
        )
        selection_fields.extend(from_location_ids)
        response_obj = get_paginated(
          my_sql_string_start + my_sql_string_end,
          selection_fields=selection_fields,
          args=request.args,
          order_clause="ORDER BY id DESC",
          order_index_format="id <= %s",
          order_arg="max_id"
        )
    elif "language" in request.args:
        selection_fields.append(request.args["language"])
        my_sql_string_end = "AND language_origin=%s"
        response_obj = get_paginated(
          my_sql_string_start + my_sql_string_end,
          selection_fields=selection_fields,
          args=request.args,
          order_clause="ORDER BY id DESC",
          order_index_format="id <= %s",
          order_arg="max_id"
        )
    else:
        return make_response(
          "No location/language query parameter", HTTPStatus.METHOD_NOT_ALLOWED
        )
    if len(response_obj.get_json()) == 0:
        # The network doesn't exist. So, let's make it!
        try:
            make_new_network(make_new_network_request())
            func_counter += 1
            if func_counter < 2:
                # We need to avoid a stack overflow error
                # if our make_new_network messes up.
                return get_networks(func_counter)
            else:
                return make_response("/networks Internal Server Error", HTTPStatus.INTERNAL_SERVER_ERROR)
        except (AttributeError, ValueError, IndexError, IntegrityError) as e:
            abort(HTTPStatus.BAD_REQUEST)
    else:
        # Just return the response object, since it is not empty.
        return response_obj


@networks.route("/<network_id>", methods=["GET"])
@require_apikey
def get_network(network_id):
    return get_by_id("networks", network_id)


@networks.route("/<network_id>/posts", methods=["GET"])
@require_apikey
def get_network_posts(network_id):
    return get_paginated("SELECT * \
                         FROM posts \
                         WHERE id_network=%s",
                         selection_fields=[network_id],
                         args=request.args,
                         order_clause="ORDER BY id DESC",
                         order_index_format="id <= %s",
                         order_arg="max_id")


@networks.route("/<network_id>/post_count", methods=["GET"])
@require_apikey
def get_network_post_count(network_id):
    query = "SELECT count(*) \
             as post_count \
             from posts \
             where id_network=%s"
    return execute_single_tuple_query(query, (network_id,))


@networks.route("/<network_id>/events", methods=["GET"])
@require_apikey
def get_network_events(network_id):
    return get_paginated("SELECT * \
                          FROM events \
                          WHERE id_network=%s",
                          selection_fields=[network_id],
                          args=request.args,
                          order_clause="ORDER BY id DESC",
                          order_index_format="id <= %s",
                          order_arg="max_id")


@networks.route("/<network_id>/users", methods=["GET"])
@require_apikey
def get_network_users(network_id):
    return get_paginated("SELECT users.*, join_date \
                          FROM network_registration \
                          INNER JOIN users \
                          ON users.id = network_registration.id_user \
                          WHERE id_network=%s",
                          selection_fields=[network_id],
                          args=request.args,
                          order_clause="ORDER BY join_date DESC",
                          order_index_format="join_date <= %s",
                          order_arg="max_registration_date")


@networks.route("/<network_id>/user_count", methods=["GET"])
@require_apikey
def get_network_user_count(network_id):
    query = "SELECT count(*) \
             as user_count \
             from network_registration \
             where id_network=%s"
    return execute_single_tuple_query(query, (network_id,))


@networks.route("/new", methods=["POST"])
@require_apikey
def make_new_network(internal_req=None):
    content_fields = [
      'city_cur', 'id_city_cur', 'region_cur', 'id_region_cur', \
      'country_cur', 'id_country_cur', 'city_origin', 'id_city_origin', \
      'region_origin', 'id_region_origin', 'country_origin', \
      'id_country_origin', 'language_origin', 'id_language_origin', \
      'network_class'
    ]

    if internal_req:
      request = internal_req

    return execute_post_by_table(request, content_fields, "networks")


@networks.route("/topTen", methods=["GET"])
def get_top_ten():
    connection = mysql.get_db()
    # For some reason, distinct only works on individual columns, so we will have to first just get the ids.
    id_cursor = connection.cursor()
    id_cursor.execute("SELECT id_network FROM networks INNER JOIN network_registration ON id=id_network \
    ORDER BY (SELECT COUNT(id_network) FROM network_registration WHERE id_network=id) DESC;")
    """
    ten_networks = []
    for id in ids:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM networks WHERE id=%s", (id['id_network'],))
        ten_networks.append(convert_objects([cursor.fetchone()], cursor.description))
    """

    return make_response(jsonify(convert_objects(id_cursor.fetchall(), id_cursor.description)), HTTPStatus.OK)