from api.apiutils import *
from api.extensions import mysql
"""
Utility module for querying events based on certain information.
"""


def get_event_id(user_id, network_id):
    """
    Precondition: user should have added an event to that network already.
    For registration purposes, we need to get the id of latest event a user added to a network.
    :param user_id: id of host
    :param network_id: id of network
    :return: id of latest event
    """
    connection = mysql.get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM events WHERE id_host=%s AND id_network=%s ORDER BY id DESC LIMIT 1",
                   (user_id, network_id))
    obj = cursor.fetchone()
    return convert_objects([obj], cursor.description)[0]["id"]
