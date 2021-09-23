import random
from sqlalchemy import or_
from flask import Flask
from flask_restful import Api, Resource, abort, fields, marshal_with, marshal
from flask_sqlalchemy import SQLAlchemy
from card_list import cards

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://syoupheng:password@localhost/21Cards_db'
db = SQLAlchemy(app)

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

class DeckResource(Resource):
    @marshal_with(deck_fields)
    def post(self):
        deck = Deck()
        db.session.add(deck)
        db.session.commit()
        return deck, 201
        
def shuffle_cards(cards, deck):
    if not deck.shuffled:
        positions = list(range(1, len(cards) + 1))
        random.shuffle(positions)
        i = 0
        for card in cards:
            card = Card(title=card['title'], type=card['type'], value=card['value'], deck_id=deck.id, position=positions[i])
            i += 1
            db.session.add(card)
        deck.shuffled = True
        db.session.commit()
    else:
        abort(403, message="This deck is already shuffled...")

class ShuffleResource(Resource):
    def post(self, deck_id):
        deck = Deck.query.filter_by(id=deck_id).first()
        if not deck:
            abort(404, message="There is no deck with this id...")
        shuffle_cards(cards, deck)
        
        return {"msg":f"The deck number {deck_id} was shuffled successfully"}, 201

def draw(deck_id):
    cards = Card.query.filter_by(deck_id=deck_id, owner=None).order_by(Card.position).all()
    if len(cards) < 52:
        abort(403, message="You already drew your cards...")
    cards[0].owner = "Player"
    cards[1].owner = "Dealer"
    cards[2].owner = "Player"
    cards[3].owner = "Dealer"
    cards[3].face_up = False
    db.session.commit()

    return cards

def calculateScore(cards):
    score = {"Player": 0, "Dealer": 0}
    num_aces_player = 0
    num_aces_dealer = 0
    for card in cards:
        if card.owner == "Player":
            if card.title == "as":
                num_aces_player += 1
                score["Player"] += 11
            else:
                score["Player"] += int(card.value)
        elif card.owner == "Dealer":
            if card.title == "as":
                num_aces_dealer += 1
                score["Dealer"] += 11
            else:
                score["Dealer"] += int(card.value)
    if (score['Player'] > 21) and (num_aces_player > 0):
        for i in range(num_aces_player):
            score["Player"] -= 10
            if score["Player"] <= 21:
                break
    
    return score
        
class DrawResource(Resource):
    def put(self, deck_id):
        deck = Deck.query.filter_by(id=deck_id).first()
        if not deck:
            abort(404, message="There is no deck with this id...")
        if not deck.shuffled:
            abort(403, message="This deck is not shuffled...")
        cards = draw(deck_id)

        score = calculateScore(cards)
        if score["Player"] == 21:
            if score["Dealer"] != 21:
                db.session.delete(deck)
                db.session.commit()
                return {
                    "msg":"You have a natural 21 ! You won !",
                    "cards":marshal(cards[:4], card_fields),
                }
            else:
                db.session.delete(deck)
                db.session.commit()
                return {
                    "msg":"This is a tie with the dealer!",
                    "cards":marshal(cards[:4], card_fields),
                }
        elif score["Dealer"] == 21:
            db.session.delete(deck)
            db.session.commit()
            return {
                "msg":"The dealer has a natural 21 ! You lost...Better luck next time !",
                "cards":marshal(cards[:4], card_fields),
            }
        return {
            "msg":"You drew 2 cards face up and the dealer drew one card face up and one card face down. Now you need to choose between ask for another card (hit) or not (stand)",
            "cards":marshal(cards[:3], card_fields)
        }

def stand(score):
    if score["Player"] > score["Dealer"]:
        msg = "Your score is higher than the dealer's. You won !" 
    elif score["Player"] < score["Dealer"]:
        msg = "Your score is lower than the dealer's. You lost...Better luck next time !",
    else:
        msg = "Your score is the same as the dealer's. This is a tie !"
    return msg

def hit(deck_id):
    new_card = Card.query.filter_by(deck_id=deck_id, owner=None).order_by(Card.position).first()
    new_card.owner = "Player"
    db.session.commit()

    return new_card

class GameResource(Resource):
    def post(self, deck_id, action):
        if action == "shuffle":
            deck = Deck.query.filter_by(id=deck_id).first()
            if not deck:
                abort(404, message="There is no deck with this id...")
            shuffle_cards(cards, deck)
            
            return {"msg":f"The deck number {deck_id} was shuffled successfully"}, 201
        else:
            abort(400, message="This action is not possible...")

    def put(self, deck_id, action):
        deck = Deck.query.filter_by(id=deck_id).first()
        if not deck:
            abort(404, message="There is no deck with this id...")
        if not deck.shuffled:
            abort(403, message="This deck is not shuffled...")
        cards = Card.query.filter(or_(Card.owner == "Player", Card.owner=="Dealer"), Card.deck_id == deck_id).order_by(Card.owner.desc()).all()
        if not cards:
            abort(400, message="You need to draw cards before choosing to stand or hit...")
        score = calculateScore(cards)
        if action == "stand":
            msg = stand(score)
            db.session.delete(deck)
            db.session.commit()
            return {
                "msg":msg,
                "Cards":marshal(cards, card_fields),
            }
        elif action == "hit":
            new_card = hit(deck_id)
            cards.append(new_card)
            cards.sort(key=lambda x: x.owner, reverse=True)
            score = calculateScore(cards)
            if score["Player"] == 21:
                db.session.delete(deck)
                db.session.commit()
                return {
                    "msg":"You have a 21 ! You won !",
                    "Cards":marshal(cards, card_fields),
                }
            elif score["Player"] > 21:
                db.session.delete(deck)
                db.session.commit()
                return {
                    "msg":"You busted ! Your score went over 21 ! Better luck next time...",
                    "Cards":marshal(cards, card_fields)
                }
            result = []
            for card in cards:
                if card.face_up:
                    result.append(card)
            result.sort(key=lambda x: x.owner, reverse=True)
            return {
                "msg": "You successfully drew a card from the deck",
                "Cards":marshal(result, card_fields),
            } 
        else:
            abort(400, message="This action is not possible...")
        
api.add_resource(DeckResource, "/deck/new")
api.add_resource(DrawResource,"/deck/<int:deck_id>/draw")
api.add_resource(GameResource,"/deck/<int:deck_id>/<string:action>")

if __name__ == "__main__":
    app.run(debug=True)