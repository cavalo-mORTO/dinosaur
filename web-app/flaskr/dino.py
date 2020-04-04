from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('dino', __name__, url_prefix='/dino')

@bp.route('/')
def index():
    name = request.args.get('name')
    if name is None:
        name = ''

    db = get_db()
    dinos = db.execute(
            'SELECT * FROM dino WHERE name LIKE ?', ('%' + name + '%',)
             ).fetchall()
    return render_template('dino/index.html', dinos=dinos, )


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        parent = request.form['parent']
        img = request.form['img']
        error = None

        if not name:
            error = 'Need a name.'

        if not content:
            error += 'Need a content.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            parent_id = db.execute(
                    'SELECT * FROM dino WHERE name = ?', (parent,)
                    ).fetchone()
            db.execute(
                    'INSERT INTO dino (name, content, img, parent_id)'
                    ' VALUES (?, ?, ?, ?)',
                    (name, content, img, parent_id,)
                    )
            db.commit()

            return redirect(url_for('dino.index'))

    return render_template('dino/create.html')

@bp.route('<int:id>/show')
def show(id):
    db = get_db()
    dino = db.execute(
            'SELECT * FROM dino WHERE id = ?', (id,)
            ).fetchone()

    data = {}
    data['img'] = dino['img']
    data['name'] = dino['name']
    data['content'] = dino['content'].split('\n')

    return render_template('dino/show.html', data=data,)
