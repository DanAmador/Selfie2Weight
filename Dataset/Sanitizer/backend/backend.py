import json
import os

from flask import request, send_file, Response, url_for, redirect
from flask_api import FlaskAPI, status
from flask_cors import CORS

from util.dataset_logger import dataset_logger as logger
from util.db.Wrappers.MongoWrapper import MongoWrapper
from util.db.model import RawEntry, SanitizedEntry, FeatureMeta

app = FlaskAPI(__name__)

CORS(app)


@app.route('/img/<image_id>', methods=["GET"])
def get_image_info(image_id):
    with db.session_scope():
        res: RawEntry = RawEntry.objects(reddit_id=image_id)
        return send_file(res["local_path"], mimetype='image/gif')


@app.route('/', methods=["GET"])
@app.route('/next/', methods=["GET"])
def start():
    return redirect(url_for("next_by", key="has_been_sanitized"))


@app.route('/next/<key>', methods=["GET"])
def next_by(key):
    with db.session_scope():

        res: RawEntry = db.get_by(RawEntry, {key: False, "has_image": True})
        if res:
            res.pop("_id")
            if "img_url" in res and "reddit_id" in res:
                res["img_url"] = url_for("get_image_info", image_id=res["reddit_id"])
            return res, status.HTTP_200_OK
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
            d = {}
            for k, v in body.items():
                features = []
                for f in v:
                    features.append(FeatureMeta(height=f["height"], width=f["width"], y=f["y"], x=f["x"]))

                    d[k] = features

                RawEntry.objects(reddit_id=image_id).update(set__raw_meta=d, set__was_preprocessed=True)
        return {}, status.HTTP_202_ACCEPTED


def mark_as_empty(image_id):
    with db.session_scope():
        rid = ""
        try:
            raw: RawEntry = RawEntry.objects(reddit_id=image_id).first()
            rid = raw.reddit_id
            os.remove(raw.local_path)
            raw.delete()
        except Exception as e:
            logger.error(e)
            logger.error(f"Can't delete {rid}")


@app.route("/img/meta/<image_id>", methods=["GET"])
def get_by_id(image_id):
    with db.session_scope():
        res = RawEntry.objects(reddit_id=image_id).first()
        return res.to_json()


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
                        RawEntry.objects(reddit_id=image_id).update(set__raw_meta=body,
                                                                    set__has_been_sanitized=True)
                return Response({}, status=201)
            else:
                mark_as_empty(image_id)
                return Response({}, status=200)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    db = MongoWrapper()
    test = {}
    app.run('0.0.0.0')
