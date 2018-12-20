from functools import wraps
from flask import request, abort
from http import HTTPStatus

from .credentials import api


def require_apikey(view_function):
    """Force an endpoint to check that a valid api key has been submitted

    This is intended to be used only for endpoints that should be only accessed
    by apps that run on servers we control (e.g. FFB, not Android). This is
    because a static API key can always be reverse-engineered out of an app
    that runs on user's devices (e.g. Android phones)

    :param view_function:
    :return:
    """
    @wraps(view_function)
    def decorated_func(*args, **kwargs):
        if request.args.get('key') and request.args.get('key') == api['key']:
            return view_function(*args, **kwargs)
        else:
            abort(HTTPStatus.UNAUTHORIZED)

    return decorated_func
