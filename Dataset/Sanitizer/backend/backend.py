from functools import wraps
from pathlib import Path
from flask import Flask
from flask import send_file, request, Response
from flask_cors import CORS, cross_origin

from Dataset.util.db.db_wrapper import DBWrapper
from Dataset.util.db.model import RawEntry, SanitizedEntry
import json
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

CORS(app)


@app.route('/img/<image_id>', methods=["GET"])
def get_image_info(image_id):
    with db.session_scope() as session:
        print(image_id)
        res: RawEntry = db.get_by(RawEntry, "reddit_id", image_id, session)
        print(res.local_path)
        return send_file(res.local_path, mimetype='image/gif')


@app.route('/next', methods=["GET"])
def next_unsanitized():
    with db.session_scope() as session:
        res: RawEntry = db.get_unsanitized(session, get_first=True)

        if res:
            return res.as_dict


def mark_as_empty(image_id, session):
    raw: RawEntry = db.get_by(RawEntry, "reddit_id", image_id, session=session)
    raw.has_been_sanitized = True
    db.save_object(raw, session=session)


@app.route("/img/<image_id>", methods=["POST"])
def save(image_id):
    try:
        body = json.loads(request.data)
        with db.session_scope() as session:
            if body:
                for entry in body:
                    meta = entry["meta"]
                    sanitized = SanitizedEntry(x=meta["x"], y=meta["y"], weight=entry["data"]["weight"],
                                               width=meta["width"], height=meta["height"], reddit_id=image_id)
                    db.save_object(sanitized, session=session)

                return Response({}, status=201)
            else:
                mark_as_empty(image_id, session)
                return Response({}, status=200)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    db = DBWrapper(Path().cwd().parent.parent / "Scrapper" / 'dump')

    # db.update(a)
    app.run()
