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
BUF_SIZE = 2 << ((10 * 1) + 4)  # 16 KB
MAX_SIZE = 2 << ((10 * 2) + 1)  # 2 MB
ALLOWED_EXTENSIONS = set(['gif', 'png', '.jpg'])
IMAGES_BASE = "https://www.culturemesh.com/user_images/"

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
    if not valid_file_type(file):
        return make_response("Invalid file format. Upload an image (.jpg, .png, or .gif)", HTTPStatus.METHOD_NOT_ALLOWED)
    # We need to safeguard against mischievous file names.
    file_name = secure_filename(file.filename)
    # Now, let's hash this image to get the directory name.
    try:
        directory_name = hash_file(file)
    except MemoryError:
        return make_response("Image too large. Upload files less than 2MB", HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
    # Cool! It looks like this file can be uploaded.
    if not os.path.exists(os.path.join(host_path['image_uploads'], directory_name)):
        # Make hash directory
        os.makedirs(os.path.join(host_path['image_uploads'], directory_name))
    # Upload image to file system
    path = os.path.join(host_path['image_uploads'], directory_name + '/' + file_name)
    file.save(path)
    # Return new url.
    return IMAGES_BASE + directory_name + "/" + file_name


def hash_file(file):
    """
    Generates a string hex hash (using md5) of the image file. We use a buffer to separate the file into
    memory-manageable chunks.
    This also throws TooLargeImageException if the file buffer manages to read more than 2MB of data.
    :param file: should be a python file.
    :return: string of hash in hex.
    """
    md5 = hashlib.md5()
    data = file.read(BUF_SIZE)
    file_size = BUF_SIZE
    while data:
        md5.update(data)
        data = file.read(BUF_SIZE)
        file_size += BUF_SIZE
        if file_size >= MAX_SIZE:
            raise MemoryError("file size too large")
    # Reset cursor for file write
    file.seek(0, 0)
    return md5.hexdigest()


def valid_file_type(file):
    """
    Checks if file type is either PNG, JPG, or GIF, which are our valid image formats.
    :param file: python file.
    :return: true if file is .png, .jpg, or .gif, false otherwise.
    """
    return file.filename.split(".")[-1] in ALLOWED_EXTENSIONS
