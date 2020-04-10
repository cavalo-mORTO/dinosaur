from app import db
import re as regexp


class Dinosaur(db.Model):
    __tablename__ = 'dinosaur'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    text = db.Column(db.String(2000))
    img = db.Column(db.String(255))
    parent_id = db.Column(db.Integer, db.ForeignKey('dinosaur.id'))

    def get_parents(self):
        parents = []
        parent = Dinosaur.query.get(self.parent_id)
        while parent is not None:
            parents.append(parent)
            parent = Dinosaur.query.get(parent.parent_id)

        return parents

    def get_contents(self):
        return Content.query.filter_by(dinosaur_id=self.id).all()

    @property
    def formatted_text(self):
        "Returns text field formatted for displaying on html"
        return self.text.split('\n')

    def __repr__(self):
        return '<Dinosaur %r>' % (self.name)


class Content(db.Model):
    __tablename__ = 'content'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.String(2000))
    dinosaur_id = db.Column(db.Integer, db.ForeignKey('dinosaur.id'))

    @property
    def formatted_text(self):
        "Returns text field formatted for displaying on html"
        return self.text.split('\n')

    @property
    def title_id(self):
        "returns title field with special chars removed"
        return regexp.sub(r'[^a-zA-Z0-9]', '', self.title or 'none')


    def __repr__(self):
        return '<Content %r>' % (self.title)
