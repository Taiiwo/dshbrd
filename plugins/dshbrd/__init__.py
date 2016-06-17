import os

from cms import app, config, save_config, plugins
from cms.api import make_error_response, make_success_response, user


@app.route('/api/plugin/dshbrd/get-cards', methods=["POST"])
def get_cards():
    dir_names = []
    for root, dirs, files in os.walk('plugins/dshbrd/cards/'):
        for dir_name in dirs:
            dir_names.append(dir_name)
    return make_success_response({'cards': dir_names})

def main(app, config):
    pass
