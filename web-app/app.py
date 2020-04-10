import os
from flask import Flask, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Dinosaur, Content
from dinosaur import bp

app.register_blueprint(bp)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello')
def hello():
    return "Hello World!"


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
