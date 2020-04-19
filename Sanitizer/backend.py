from pathlib import Path

from flask import send_file
from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

p = Path().cwd().parent / "Scrapper" / 'dump' / "img"


@app.route('/img/<id>')
@cross_origin()
def get_image(id):
    return send_file(p / (id + ".jpg"), mimetype='image/jpg')


if __name__ == '__main__':
    app.run()
