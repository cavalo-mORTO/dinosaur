from flask import (
        flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from app import db
from models import Dinosaur, Content
from dinosaur import bp

@bp.route('/')
def index():
    name = request.args.get('name') or ''
    page = request.args.get('page', 1, type=int)

    data = Dinosaur.query.filter(
            Dinosaur.name.like(name + '%')
            ).paginate(page, 21, False)

    next_url = url_for('dinosaur.index', page=data.next_num, name=name) \
            if data.has_next else None
    prev_url = url_for('dinosaur.index', page=data.prev_num, name=name) \
            if data.has_prev else None

    if not data.items:
        abort(404)

    return render_template('dinosaur/index.html',
            dinos=data.items,
            next_url=next_url,
            prev_url=prev_url)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        error = None

        data = request.json
        name = data['name']
        contents = data['content']
        parent = data['parent']
        img = data['img']


        exists = Dinosaur.query.filter_by(name=name).first()

        if exists:
            error = 'Dinosaur already exists.'
        elif not name:
            error = 'Need a name.'
        elif not contents:
            error = 'Need contents.'

        if error is not None:
            flash(error)
        else:
            parent = Dinosaur.query.filter_by(name=parent).first()

            try:
                parent_id = parent.id
            except AttributeError:
                parent_id = None

            dino = Dinosaur(name=name, text=contents[0].get('text'), img=img, parent_id=parent_id)

            db.session.add(dino)
            db.session.commit()


            for c in contents[1:]:
                cont = Content(title=c.get('title'), text=c.get('text'), dinosaur_id=dino.id)
                db.session.add(cont)
            db.session.commit()


            return redirect(url_for('dinosaur.index'))

    return render_template('dinosaur/create.html')

@bp.route('<int:id>/show')
def show(id):

    data = Dinosaur.query.get(id)

    if data is None:
        abort(404)

    return render_template('dinosaur/show.html', data=data,)
