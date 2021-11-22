import json
from uuid import UUID

from flask import Flask, Response
from flask import request
from flask_cors import CORS

import service

app = Flask(__name__)
CORS(app)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


@app.route("/")
def index():
    return "Hello World!"


@app.route("/startTest", methods=["POST"])
def start_test():
    json_request = request.get_json()
    start_test_response = service.start_executing_test(json_request)

    return Response(json.dumps(start_test_response, cls=UUIDEncoder), status=200, mimetype='application/json')


@app.route("/testStatus", methods=["POST"])
def test_status():
    json_request = request.get_json()
    response = service.get_test_handle_status(json_request["test_handle_id"])
    return Response(json.dumps(response, cls=UUIDEncoder), status=200, mimetype='application/json')


@app.route("/testResults", methods=["POST"])
def test_results():
    json_request = request.get_json()
    response = service.get_test_results(json_request["test_handle_id"])
    return Response(json.dumps(response, cls=UUIDEncoder), status=200, mimetype='application/json')


@app.route("/allTests")
def all_test_results():
    response = service.get_all_test_results()
    return Response(json.dumps(response, cls=UUIDEncoder), status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True)
