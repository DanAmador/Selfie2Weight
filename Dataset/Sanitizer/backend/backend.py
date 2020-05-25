import json
from pathlib import Path

from flask import Flask
from flask import send_file, request, Response
from flask_cors import CORS

from util.db.Wrappers.MongoWrapper import MongoWrapper
from util.db.model import RawEntry, SanitizedEntry
from util.dataset_logger import dataset_logger as logger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

CORS(app)


@app.route('/img/<image_id>', methods=["GET"])
def get_image_info(image_id):
    with db.session_scope() as session:
        res: RawEntry = db.get_by(RawEntry, "reddit_id", image_id, session)
        return send_file(res.local_path, mimetype='image/gif')


@app.route('/next', methods=["GET"])
def next_unsanitized():
    with db.session_scope() as session:
        res: RawEntry = db.get_unsanitized(session, get_first=True)

        if res:
            return res.as_dict
        else:
            logger.error("Could not find next unsanitized")
            return {}


def mark_as_empty(image_id, session):
    raw: RawEntry = db.get_by(RawEntry, "reddit_id", image_id, session=session)
    raw.has_been_sanitized = True
    db.save_object(raw)


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
                    db.save_object(sanitized)

                return Response({}, status=201)
            else:
                mark_as_empty(image_id, session)
                return Response({}, status=200)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    db = MongoWrapper()
    app.run()
