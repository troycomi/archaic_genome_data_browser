from flask import Blueprint

bp = Blueprint('main', __name__)

from archaic_genome_data_browser.main import routes  # noqa
