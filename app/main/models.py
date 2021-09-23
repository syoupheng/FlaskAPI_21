from flask_restful import fields
from database import db

class Deck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cards = db.relationship('Card', backref='deck', cascade="all, delete", lazy=True)
    shuffled = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Deck number {self.id}"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    value = db.Column(db.String(10), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.String(10), nullable=True)
    face_up = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"Card {self.title} of {self.type} belongs to deck {self.deck_id}"

deck_fields = {
    'id': fields.Integer,
    'shuffled': fields.Boolean,
}

card_fields = {
    'title': fields.String,
    'type': fields.String,
    'value': fields.String,
    'owner': fields.String,
}