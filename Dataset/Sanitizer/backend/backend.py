from pathlib import Path
from flask import Flask
from flask import send_file, request
from flask_cors import CORS, cross_origin

from Dataset.util.data_classes import RawEntry
from Dataset.util.db_wrapper import DBWrapper
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

CORS(app)
db = SQLAlchemy(app)

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


import random


@app.route("/img/<image_id>", methods=["POST"])
def save(image_id):
    try:
        body = json.loads(request.data)
        # df = df.loc[df["id"] == image_id, "sanitized"]
    except Exception as e:
        print(e)

    #     TODO crop image from request info
    return df.loc[df["sanitized"] == False].iloc[random.randint(0, 20)].to_json()


if __name__ == '__main__':
    db = DBWrapper(Path().cwd().parent.parent / "Scrapper" / 'dump')

    db.update(a)
    # app.run()
