from models import Deck
from flask_restful import abort
from database import db

def create_deck():
    deck = Deck()
    db.session.add(deck)
    db.session.commit()

    return deck

def delete_deck(deck):
    db.session.delete(deck)
    db.session.commit()

def check_deck_exists(deck):
    if not deck:
        abort(404, message="There is no deck with this id...")

def check_deck_is_shuffled(deck):
    if not deck.shuffled:
        abort(403, message="This deck is not shuffled...")