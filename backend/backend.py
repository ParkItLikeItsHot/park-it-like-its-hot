#!/usr/bin/env python3

import json
import logging
from pathlib import Path
import flask


app = flask.Flask(__name__, static_folder="../pilih-frontend/dist")
logger = logging.getLogger(__name__)


class Lot:
    name: str
    short_name: str
    fill_level: int

    def __init__(self, name: str, short_name: str):
        self.name = name
        self.short_name = short_name
        self.fill_level = 0


class ParkingLots:
    lots: list[Lot]

    def __init__(self):
        self.lots = []


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path: str):

    if app.static_folder == None:
        return '{"error": "Static folder not set"}', 500

    if path != "" and Path(app.static_folder).joinpath(path).exists():
        return flask.send_from_directory(app.static_folder, path)
    else:
        return flask.send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(debug=True)
