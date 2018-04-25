from flask import Flask
from .decorators import require_apikey

api = Flask(__name__)

# Register API submodules (aka blueprints)

from api.blueprints.users.controllers import users
from api.blueprints.networks.controllers import networks
from api.blueprints.posts.controllers import posts
from api.blueprints.events.controllers import events
from api.blueprints.locations.controllers import locations
from api.blueprints.languages.controllers import languages
from api.blueprints.accounts.controllers import accounts

api.register_blueprint(users, url_prefix='/user')
api.register_blueprint(networks, url_prefix='/network')
api.register_blueprint(posts, url_prefix='/post')
api.register_blueprint(events, url_prefix='/event')
api.register_blueprint(locations, url_prefix='/location')
api.register_blueprint(languages, url_prefix='/language')
api.register_blueprint(accounts, url_prefix='/account')
