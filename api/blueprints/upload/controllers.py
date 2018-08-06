#enable imports from dir above ... we need to get credentials.
import os
from api.credentials import host_path
from flask import Blueprint, request, make_response
from http import HTTPStatus
from api import require_apikey
from api.apiutils import hash_file, valid_file_type

from werkzeug.utils import secure_filename

upload = Blueprint('upload', __name__)

IMAGES_BASE = "https://www.culturemesh.com/user_images/"


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

