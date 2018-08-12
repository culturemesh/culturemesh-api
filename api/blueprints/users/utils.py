from api.apiutils import *
from api.extensions import mysql
import random
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


def generate_user_name():
    """
    Generates user names for each user with a NULL username field.
    """
    connection = mysql.get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username IS NULL")
    users_obj = convert_objects(cursor.fetchall(), cursor.description)
    cursor.close()
    counter = random.randint(1, 101)
    for user in users_obj:
        # Set username. It will be
        # [first letter of firstname][lastname without spaces/special charcters][a number to differentiate]
        user_name = ""
        if 'first_name' in user and user['first_name'] is not None:
            user_name += user["first_name"][:1]
        if 'last_name' in user and user['last_name'] is not None:
            # https://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
            user_name += ''.join(e for e in user["last_name"] if e.isalnum())
        user_name += str(counter)
        counter += 1
        put_cursor = connection.cursor()
        put_cursor.execute("UPDATE users SET username=%s WHERE id=%s", (user_name, user['id']))
        connection.commit()
    return make_response("OK", HTTPStatus.OK)


def add_user_to_event(user_id, event_id, role):
    """
    Registers user to an event.
    :param user_id: id of user
    :param event_id: id of event
    :param role: either "host" or "guest"
    """
    connection = mysql.get_db()
    event_registration_cursor = connection.cursor()
    event_registration_cursor.execute("INSERT INTO event_registration VALUES (%s,%s,CURRENT_TIMESTAMP, %s)",
                                      (user_id, event_id, role))
    connection.commit()
