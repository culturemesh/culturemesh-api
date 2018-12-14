from flask import Blueprint
from api import api

dev = Blueprint('dev', __name__)

"""Developer tools for debugging

These endpoints should be safe to expose publicly from a security standpoint,
but they should also not be accessible from the user interface.

"""


@dev.route("/note")
def get_note():
    """Returns the contents of the note file for debugging

    The note file is specified by the ``NOTE_PATH`` configuration option.

    :return: Contents of note file as raw text
    """
    with open(api.config["NOTE_PATH"], 'r') as file:
        return file.read()
