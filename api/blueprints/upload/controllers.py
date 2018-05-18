import os
from ...credentials import host_path
from flask import Blueprint, request, make_response
from http import HTTPStatus
from api import require_apikey
from werkzeug.utils import secure_filename

upload = Blueprint('upload', __name__)


@upload.route("/ping")
@require_apikey
def test():
    print(" THE REAL FLASK PATH  ")
    print(os.path)
    with open("Output.txt", "w") as text_file:
        text_file.write("Purchase Amount: %s" % TotalAmount)
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
    #file = request.files['file']
    # We need to safeguard against mischievous file names.
    #file_name = secure_filename(file.name)
    #file.save(os.path)
    with open(host_path+"file_write_test.txt", "w") as text_file:
        text_file.write("Drew wrote with flask!!")
    # TODO: Fetch image binary

    # TODO: Upload image to file system.
    # TODO: Return new url.
    return "pong"