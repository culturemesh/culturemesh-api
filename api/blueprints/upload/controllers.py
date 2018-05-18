import os

from flask import Blueprint, request, make_response
from http import HTTPStatus
from api import require_apikey
from werkzeug.utils import secure_filename


upload = Blueprint('upload', __name__)


@upload.route("/ping")
@require_apikey
def test():
    print(" FLASK PATH " + str(os.path))
    return "pong"


@upload.route("/image", methods=["POST"])
@require_apikey
def upload_image():
    """
    This function uploads the image to the BlueHost filesystem. The request body should be multipart/formdata,
    with only one key-value pair: key - 'file'       value - image binary
    :return: The request will return the url
    """
    if request.files is None:
        return make_response("No image in request body.", HTTPStatus.METHOD_NOT_ALLOWED)
    file = request.files['file']
    # We need to safeguard against mischievous file names.
    file_name = secure_filename(file.name)
    file.save(os.path)

    # TODO: Fetch image binary
    request.files['file']
    os.sa
    # TODO: Upload image to file system.
    # TODO: Return new url.