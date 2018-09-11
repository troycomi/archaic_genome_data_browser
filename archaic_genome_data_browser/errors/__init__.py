from flask import Blueprint

bp = Blueprint('errors', __name__)

from archaic_genome_data_browser.errors import handlers  # noqa
