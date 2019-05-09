"""
This module contains a web proxy
"""

import os

import requests
from dotenv import load_dotenv
from flask import Flask
from flask import Response
from flask import request
from werkzeug.middleware.proxy_fix import ProxyFix


APP = Flask(__name__)
APP.wsgi_app = ProxyFix(APP.wsgi_app)


@APP.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@APP.route("/<path:path>", methods=["GET", "POST"])
def proxy(path):
    """
    This method proxies all requests to BACKEND
    """
    print(request.method, path, request.headers, request.get_data())
    resp = requests.request(
        method=request.method,
        url=os.environ.get("BACKEND") + path,
        headers={
            key: value
            for (key, value) in request.headers
            if key in ["Authorization", "Content-Type"]
        },
        data=request.get_data(),
    )
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    print(resp.content, resp.status_code, headers)
    response = Response(resp.content, resp.status_code, headers)
    return response


if __name__ == "__main__":
    load_dotenv()
    APP.run(host="0.0.0.0", port=os.environ.get("PORT", 8080))
