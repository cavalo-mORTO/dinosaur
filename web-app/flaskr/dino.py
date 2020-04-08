import re as regexp

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
    dinos = db.execute('''
            SELECT d.id, name, img, text
            FROM dino d LEFT JOIN content c ON c.dino_id = d.id
            WHERE d.id IN (SELECT id FROM dino WHERE name LIKE ?)
            GROUP BY d.id ''', (name + '%',)
            ).fetchall()

    if not dinos:
        abort(404)

    return render_template('dino/index.html', dinos=dinos, )

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        error = None

        data = request.json
        name = data['name']
        contents = data['content']
        parent = data['parent']
        img = data['img']


        db = get_db()
        exists = db.execute(
                'SELECT * FROM dino WHERE name = ?', (name,)
                ).fetchone()

        if exists:
            error = 'Dinosaur already exists.'
        elif not name:
            error = 'Need a name.'
        elif not contents:
            error = 'Need contents.'

        if error is not None:
            flash(error)
        else:
            parent = db.execute(
                    'SELECT * FROM dino WHERE name = ?', (parent,)
                    ).fetchone()

            try:
                parent_id = parent['id']
            except TypeError:
                parent_id = None

            dino = db.execute(
                    'INSERT INTO dino (name, img, parent_id)'
                    ' VALUES (?, ?, ?)',
                    (name, img, parent_id,)
                    )
            db.commit()


            for c in contents:
                db.execute(
                        'INSERT INTO content (title, text, dino_id)'
                        ' VALUES (?, ?, ?)',
                        (c['title'], c['text'], dino.lastrowid,)
                        )
            db.commit()

            return redirect(url_for('dino.index'))

    return render_template('dino/create.html')

@bp.route('<int:id>/show')
def show(id):
    db = get_db()
    contents = db.execute('''
            SELECT name, img, title, text, parent_id
            FROM dino d LEFT JOIN content c ON c.dino_id = d.id
            WHERE d.id = ? ''', (id,)
            ).fetchall()

    if not contents:
        abort(404)

    parents = []
    p = db.execute('SELECT * FROM dino WHERE id = ?', (contents[0]['parent_id'],)).fetchone()
    while p is not None:
        parents.append(p)
        p = db.execute('SELECT * FROM dino WHERE id = ?', (p['parent_id'],)).fetchone()


    data = {}
    data['parents'] = parents
    data['img'] = contents[0]['img']
    data['name'] = contents[0]['name']

    data['content'] = [
            x for x in map(
                lambda d:
                {
                    'title_id': regexp.sub(r'[^a-zA-Z0-9]', '', d['title'] or 'none'),
                    'title': d['title'],
                    'text': d['text'].split('\n')
                }, contents)
            ]

    return render_template('dino/show.html', data=data,)
