#!/usr/bin/env python3

import requests
from ipaddress import IPv4Address
import json
import logging
from pathlib import Path
import threading
import time
import flask
from flask.globals import request


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

    def set_fill(self, fill_level: int):
        self.fill_level = fill_level

    def to_dict(self) -> object:
        return {
            'short_name': self.short_name,
            'name': self.name,
            'fill_level': self.fill_level
        };
    

class ParkingLots:
    lots: list[Lot]

    def __init__(self):
        self.lots = []

    def add_lot(self, name: str, short_name: str):
        self.lots.append(Lot(name, short_name))
    
    def get_lot(self, n: int):
        return self.lots[n]

    def get_lot_by_name(self, name: str):
        for lot in self.lots:
            if lot.name == name:
                return lot
        return None

    def get_lot_by_short_name(self, name: str):
        for lot in self.lots:
            if lot.name == name:
                return lot
        return None

    def update_fill(self, fill_level: int, short_name: str | None, name: str | None):
        if short_name != None:
            



@app.route("/get-lot")
def get_fill():
    if not flask.request.is_json:
        return {"error": "Request was not JSON"}, 400 
    
    lot_json = request.get_json()
    
    if lot_json["short_name"]:
        lot = lots.get_lot_by_short_name(lot_json["short_name"]) 
        if lot != None:
            return json.dumps(lot.to_dict()) 
    elif lot_json["name"]:
        lot = lots.get_lot_by_name(lot_json["name"])
        if lot != None:
            return json.dumps(lot.to_dict()) 

    return json.dumps({"error": "Could not find lot"}), 400




@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_static(path: str):
        
    if app.static_folder == None:
        return '{"error": "Static folder not set"}', 500

    if path != "" and Path(app.static_folder).joinpath(path).exists():
        return flask.send_from_directory(app.static_folder, path)
    else:
        return flask.send_from_directory(app.static_folder, "index.html")

lots = ParkingLots()

def update_lots(servers: list[str]):
    while True:
        logger.info("impl update_lots")
       
        for server in servers:
            res = requests.get(server + '/update')
            if res.status_code != 200:
                logger.error(f"failed get from {server} with code {res.status_code}")
                continue
            try:
                data = res.json()
            except json.JSONDecodeError:
                logger.error(f"response from {server} was not valid json")
                continue
                
            if data['fill_level'] == None:
                logger.error(f"response from {server} did not provide fill level")
                continue

            if data['short_name'] != None:
                lots.update_fill(data['fill_level'], short_name=data['short_name'])
            elif data['name'] != None:
                lots.update_fill(data['fill_level'], name=data['name'])
            else:
                logger.error(f"response from {server} did not provide a name or short_name")
                continue


        time.sleep(120)
        pass

if __name__ == "__main__":
    addrs = ["127.0.0.1:6969"]
    threading.Thread(target=update_lots, args=(addrs)).start()
    
    app.run(debug=True)    

if __name__ == "__main__":
    app.run(debug=True)
