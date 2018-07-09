from flask import Blueprint
from api import require_apikey
from flask_login import UserMixin, login_manager, login_user

accounts = Blueprint('account', __name__)

@accounts.route("/ping")
@require_apikey
def test():
    return "pong"


def validate_user(email_or_username, password):
    # TODO
    return -1


@accounts.route("/verify_account/<email_or_username>/<password>", methods=["GET"])
@require_apikey
def verify_account(email_or_username, password):
    user_id = validate_user(email_or_username, password)
    if user_id != -1:
        user = load_user(user_id)
        login_user(user)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


class User(UserMixin):
    """
    This user class is used by Flask Login to validate users.
    """