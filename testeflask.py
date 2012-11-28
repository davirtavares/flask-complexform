# -*- coding: UTF-8 -*-
# vim: set ts=4 sw=4 expandtab :

from flask import Flask, Response, jsonify, request, abort

import complexform

app = Flask(__name__)
app.request_class = complexform.ComplexFormRequest

@app.route("/", methods=["GET", "POST", "PATCH", "DELETE"])
def index():
    print "REQUEST"

    import pdb; pdb.set_trace()

    return "OK"

if __name__ == '__main__':
    app.run()
