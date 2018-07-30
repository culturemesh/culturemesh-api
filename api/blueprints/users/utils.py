from api.apiutils import *
from api.extensions import mysql
"""
Utility module for querying users based on certain information.
"""



def get_user_by_email(email):
    """
    Checks database and returns object representing user with that username.
    :param email: email of CultureMesh account (string)
    :return: user_obj from db or None if no corresponding found.
    """
    connection = mysql.get_db()
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(query, (email,))
    user_db_tuple = cursor.fetchone()
    if user_db_tuple is None:
        return None
    user = convert_objects([user_db_tuple], cursor.description)[0]
    cursor.close()
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
    connection = mysql.get_db()
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE username=%s"
    cursor.execute(query, (username,))
    user_db_tuple = cursor.fetchone()
    if user_db_tuple is None:
        return None
    user = convert_objects([user_db_tuple], cursor.description)[0]
    cursor.close()
    return user