#enable imports from dir above ... we need to get credentials.
import os
from api.credentials import host_path
from flask import Blueprint, request, make_response
from http import HTTPStatus
from api import require_apikey
import hashlib

from werkzeug.utils import secure_filename

upload = Blueprint('upload', __name__)

# Our buffer size for file reads is
BUF_SIZE = 2<<(10 * 3)

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
    file_name = secure_filename(file.filename)
    # Now, let's hash this image to get the directory name.
    directory_name = hash_file(file)
    # Upload image to file system.
    # Make hash directory
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    path = os.path.join(host_path['image_uploads'], directory_name + '/' + file_name)
    file.save(path)
    # Return new url.
    return path


def hash_file(file):
    """
    Generates a string hex hash (using md5) of the image file. We use a buffer to separate the file into
    memory-manageable chunks.
    :param file: should be a python file.
    :return: string of hash in hex.
    """
    md5 = hashlib.md5()
    data = file.read(BUF_SIZE)
    while data:
        md5.update(data)
        data = file.read(BUF_SIZE)
    return md5.hexdigest()
