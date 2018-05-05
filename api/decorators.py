from functools import wraps
from flask import request, abort
from http import HTTPStatus

from .credentials import api


def require_apikey(view_function):
    @wraps(view_function)
    def decorated_func(*args, **kwargs):
        if request.args.get('key') and request.args.get('key') == api['key']:
            return view_function(*args, **kwargs)
        else:
            abort(HTTPStatus.UNAUTHORIZED)

    return decorated_func
