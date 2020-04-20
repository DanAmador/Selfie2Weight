from pathlib import Path

import pandas as pd
from flask import Flask
from flask import send_file, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

p = Path().cwd().parent / "Scrapper" / 'dump'

df = {}


@app.route('/img/<image_id>', methods=["GET"])
@cross_origin()
def get_image(image_id):
    return send_file(p / "img" / (image_id + ".jpg"), mimetype='image/jpg')


@app.route('/img/<image_id>/info')
@cross_origin()
def get_image_info(image_id):
    return df.loc[df["id"] == image_id].iloc[0].to_json()


@app.route('/next')
def next_unsanitized():
    gen = df.loc[df["sanitized"] == False]
    return gen.iloc[0].to_json()


@app.route("/save", methods=["POST"])
def save():
    body = request.data
    if "id" in body:
        df.loc[df["id"] == body["id"], "sanitized"] = True
        # TODO crop image from request info
    return request.data


if __name__ == '__main__':
    df = pd.read_csv(p / "data.csv")

    app.run()
