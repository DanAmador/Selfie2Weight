import json

from flask import request, send_file, Response, url_for, redirect
from flask_api import FlaskAPI, status
from flask_cors import CORS

from util.dataset_logger import dataset_logger as logger
from util.db.Wrappers.MongoWrapper import MongoWrapper
from util.db.model import RawEntry, SanitizedEntry

app = FlaskAPI(__name__)

CORS(app)


@app.route('/img/<image_id>', methods=["GET"])
def get_image_info(image_id):
    with db.session_scope():
        res: RawEntry = db.get_by(RawEntry, {"reddit_id": image_id}, )
        return send_file(res.local_path, mimetype='image/gif')


@app.route('/next/', methods=["GET"])
def next():
    return redirect(url_for("next_by", key="has_been_sanitized"))


@app.route('/next/<key>', methods=["GET"])
def next_by(key):
    with db.session_scope():

        res: RawEntry = db.get_by(RawEntry, {key: False} )
        if len(res) > 0:
            if "img_url" in res:
                res.img_url = url_for("get_image_info", image_id=res.reddit_id)
            t = res[0]
            t.pop("_id")
            return t
        else:
            if key == "was_preprocessed":
                logger.info("All images in db were preprocessed")
                return {}, status.HTTP_204_NO_CONTENT
            logger.error(f"Could not find next {key}")
            return {}


@app.route("/meta/<image_id>", methods=["POST"])
def save_meta(image_id):
    body = request.data
    if body:
        with db.session_scope():
            raw: RawEntry = db.get_by(RawEntry, {"reddit_id": image_id}, )
            raw.raw_meta = body
            raw.has_been_sanitized = True
            db.save_object(raw)
    return {}, status.HTTP_202_ACCEPTED


def mark_as_empty(image_id):
    raw: RawEntry = db.get_by(RawEntry, {"reddit_id": image_id}, )
    raw.has_been_sanitized = True
    db.save_object(raw)


@app.route("/img/<image_id>", methods=["POST"])
def save(image_id):
    try:
        body = request.data
        with db.session_scope():
            if body:
                for entry in body:
                    meta = entry.get("meta", None)
                    if meta:
                        sanitized = SanitizedEntry(x=meta["x"], y=meta["y"], weight=entry["data"]["weight"],
                                                   width=meta["width"], height=meta["height"], reddit_id=image_id)
                        db.save_object(sanitized)

                return Response({}, status=201)
            else:
                mark_as_empty(image_id)
                return Response({}, status=200)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    db = MongoWrapper()
    app.run('0.0.0.0')
