from flask import jsonify, make_response
from api.extensions import mysql
from http import HTTPStatus

"""
Contains utility routines for API controller logic. Mostly
dirty work and repeated logic.
"""

def convert_objects(tuple_arr, description):
    """
    A DB cursor returns an array of tuples, without attribute names.
    This function converts these tuples into objects
    with key-value pairs.
    :param tuple_arr:  An array of tuples
    :param description: The cursor's description, which allows you to find the attribute names.
    :return: An array of objects with attribute names according to key-value pairs"""
    obj_arr = []
    for tuple_obj in tuple_arr:
        obj_arr.append({description[index][0]: column for index, column in enumerate(tuple_obj)})
    return obj_arr

def make_response_from_single_tuple(cursor):
    """
    Given a database cursor from which we expect only one result to be
    returned, extracts that tuple into an object and makes a response
    from it.

    If there are no results in the cursor, this method also returns
    the correct response.

    NOTE: the cursor must be closed by the caller.

    :param cursor: A 'loaded' cursor
    :return: A response object ready to return to the client
    """
    obj = cursor.fetchone()
    if obj is not None:
        obj = convert_objects([obj], cursor.description)[0]
    status = HTTPStatus.METHOD_NOT_ALLOWED if obj is None else HTTPStatus.OK
    return make_response(jsonify(obj), status)

def get_by_id(table_name, id):
    """
    Given a table name and an id to search for, queries the table
    and returns a response object ready to be returned to the client.

    :param table_name: The name of the table to query
    :param id: The id of the object to fetch
    :returns: A response object ready to return to the client.
    """
    connection = mysql.get_db()
    cursor = connection.cursor()

    # Note table_name is never supplied by a client, so we do not
    # need to escape it.
    query_str = ('SELECT * \
                 FROM %s \
                 WHERE id=' % table_name)
    cursor.execute(query_str[0] + '%s', (id,))
    response = make_response_from_single_tuple(cursor)
    cursor.close()
    return response

def event_exists(event_id):
    """
    This function is used to validate endpoint input.
    This function checks if the passed event id is a valid event id
    (there is a corresponding event with that id.)
    :param event_id: the event id.
    :return: true if valid, false if no event found.
    """
    connection = mysql.get_db()
    event_registration_check_cursor = connection.cursor()
    event_registration_check_cursor.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    possible_event = event_registration_check_cursor.fetchone()
    event_registration_check_cursor.close()
    return possible_event is not None


def user_exists(user_id):
    """
     This function is used to validate endpoint input.
     This function checks if the passed user id is a valid user id
    (there is a corresponding user with that id.)
    :param user_id:
    :return: true if valid, false if no user found.
    """
    connection = mysql.get_db()
    user_check = connection.cursor()
    user_check.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    possible_user = user_check.fetchone()
    user_check.close()
    return possible_user is not None


def network_exists(network_id):
    """
    This function is used to validate endpoint input.
    This function checks if the passed network id is a valid
    network id (there is a corresponding network with that id.)
    :param network_id:
    :return: true if valid, false if no network found.
    """
    connection = mysql.get_db()
    network_check = connection.cursor()
    network_check.execute("SELECT * FROM networks WHERE id=%s", (network_id,))
    possible_network = network_check.fetchone()
    network_check.close()
    return possible_network is not None
