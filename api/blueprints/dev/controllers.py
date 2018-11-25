from flask import Blueprint
import os

dev = Blueprint('dev', __name__)


@dev.route("/note")
def get_note():
    path = os.path.abspath(__file__)
    dir = os.path.dirname(path)
    note_path = os.path.join(dir, "note.txt")
    with open(note_path, 'r') as file:
        return file.read()


@dev.route("/print")
def print_out():
    line = "Printed from api/dev/controllers.py/print_out"
    print(line)
    return "The following line was printed: '{}'".format(line)
