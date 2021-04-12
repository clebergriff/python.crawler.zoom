# encoding: utf-8

from flask import Flask
from flask import request
from main2 import getSource

app = Flask(__name__)


@app.route("/", methods=['GET'])
def root_get():
    print("Accessing data..")

    try:
        keyword = request.args.get('q')
        result = getSource(keyword, 1)
        return result
    except Exception as e:
        return print(e)


if __name__ == "__main__":
    app.run()
