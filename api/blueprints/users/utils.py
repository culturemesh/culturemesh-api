from api.apiutils import *
from api.extensions import mysql
from flask import g
"""
Utility module for querying users based on certain information.
"""


def get_user_by_email(email):
    """
    Checks database and returns object representing user with that username.
    :param email: email of CultureMesh account (string)
    :return: user_obj from db or None if no corresponding found.
    """
    query = "SELECT * FROM users WHERE email=%s"
    item, desc = execute_get_one(query, (email,))
    if item is None:
        return None
    user = convert_objects([item], desc)[0]
    return user


def get_user_by_id(id):
    """
    Checks database and returns object representing user with that id.
    :param id: id of CultureMesh account (string)
    :return: user_obj from db or None if no corresponding found.
    """
    connection = mysql.get_db()
    cursor = connection.cursor()
    # Note table_name is never supplied by a client, so we do not
    # need to escape it.
    query = "SELECT * FROM users WHERE id=%s"
    cursor.execute(query, (id,))
    user_db_tuple = cursor.fetchone()
    if user_db_tuple is None:
        return None
    user = convert_objects([user_db_tuple], cursor.description)[0]
    cursor.close()
    return user


def get_user_by_username(username):
    """
    Checks database and returns object representing user with that id.
    :param username: id of CultureMesh account (string)
    :return: user_obj from db or None if no corresponding found.
    """
    query = "SELECT * FROM users WHERE username=%s"
    item, desc = execute_get_one(query, (username,))
    if item is None:
        return None
    user = convert_objects([item], desc)[0]
    return user


def _add_user_to_event(user_id, event_id, role):
    """
    Registers user to an event.
    :param user_id: id of user
    :param event_id: id of event
    :param role: either "host" or "guest"
    """
    args = (user_id, event_id, role)
    query = "INSERT INTO event_registration VALUES " \
            "(%s,%s,CURRENT_TIMESTAMP, %s)"
    execute_insert(query, args)


def _remove_user_from_event(user_id, event_id):
    """
    Removes a user-event pair from the event_registration table.
    :param user_id: id of user.
    :param event_id: id of event
    """
    query = "DELETE FROM event_registration WHERE id_event=%s AND id_guest=%s"
    args = (event_id, user_id)
    execute_mod(query, args)


def get_curr_user_id():
    return g.user.id
