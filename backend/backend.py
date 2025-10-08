#!/usr/bin/env python3

import logging
from pathlib import Path
import flask

app = flask.Flask(__name__, static_folder='../pilih-frontend/dist')
logger = logging.getLogger(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path: str):

    if app.static_folder == None:
        return '{"error": "Static folder not set"}', 500

    if path != "" and Path(app.static_folder).joinpath(path).exists():
        return flask.send_from_directory(app.static_folder, path)
    else:
        return flask.send_from_directory(app.static_folder, 'index.html')
    




if __name__ == "__main__":
    app.run(debug=True)    

