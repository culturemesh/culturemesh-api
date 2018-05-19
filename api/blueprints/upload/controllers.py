#enable imports from dir above ... we need to get credentials.
import os
from api.credentials import  host_path
from flask import Blueprint, request, make_response
from http import HTTPStatus
from api import require_apikey
import hashlib

from werkzeug.utils import secure_filename

upload = Blueprint('upload', __name__)


@upload.route("/ping")
@require_apikey
def test():
    print(" THE REAL FLASK PATH  ")
    print(os.path)
    with open(host_path['image_uploads']+"file_write_test.txt", "w") as text_file:
        text_file.write("Drew wrote with flask!!")
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
    # Fetch image binary
    file = request.files['file']
    # We need to safeguard against mischievous file names.
    file_name = secure_filename(file.name)
    # Upload image to file system.
    path = os.path.join(host_path['image_uploads'], hashlib.md5(file_name.encode('utf-8')).hexdigest() + "/" + file_name)
    file.save(path)
    # Return new url.
    return path
