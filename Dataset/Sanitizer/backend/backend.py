from functools import wraps
from pathlib import Path
from flask import Flask
from flask import send_file, request
from flask_cors import CORS, cross_origin

from Dataset.util.db.db_wrapper import DBWrapper
from Dataset.util.db.model import RawEntry
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

CORS(app)


@app.route('/img/<image_id> ')
def get_image_info(image_id, ):
    with db.session_scope() as session:
        res = db.get_by(RawEntry, "reddit_id", image_id, session)
        return res.as_dict


@app.route('/next')
def next_unsanitized(**kwargs):
    with db.session_scope() as session:
        res = db.get_unsanitized(session, all=False)
        return res.as_dict


@app.route("/img/<image_id>", methods=["POST"])
def save(image_id):
    try:
        body = json.loads(request.data)
        # df = df.loc[df["id"] == image_id, "sanitized"]
    except Exception as e:
        print(e)

    # #     TODO crop image from request info
    # return df.loc[df["sanitized"] == False].iloc[random.randint(0, 20)].to_json()


if __name__ == '__main__':
    db = DBWrapper(Path().cwd().parent.parent / "Scrapper" / 'dump')

    # db.update(a)
    app.run()
