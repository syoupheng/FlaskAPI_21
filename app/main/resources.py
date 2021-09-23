from flask_restful import marshal_with, Resource, abort, marshal, Api
from card_list import cards as card_list
from models import deck_fields, Deck, Card, card_fields
from deck_service import create_deck, check_deck_is_shuffled, check_deck_exists, delete_deck, delete_deck
from card_service import shuffle_cards, calculateScore, get_draw_result, get_hit_result, check_cards_drawn, hit, stand
from sqlalchemy import or_

class DeckResource(Resource):
    @marshal_with(deck_fields)
    def post(self):
        deck = create_deck()
        return deck, 201

class GameResource(Resource):
    def post(self, deck_id, action):
        if action == "shuffle":
            shuffle_cards(card_list, deck_id)           
            return {"msg":f"The deck number {deck_id} was shuffled successfully"}, 201
        else:
            abort(400, message="This action is not possible...")

    def put(self, deck_id, action):
        deck = Deck.query.filter_by(id=deck_id).first()
        check_deck_exists(deck)
        check_deck_is_shuffled(deck)
        cards = Card.query.filter(or_(Card.owner == "Player", Card.owner=="Dealer"), Card.deck_id == deck_id).order_by(Card.owner.desc()).all()
        score = calculateScore(cards)
        if action == "draw":
            return get_draw_result(deck, score)
        if action == "stand":
            check_cards_drawn(cards)
            msg = stand(score)
            delete_deck(deck)
            return {
                "msg":msg,
                "Cards":marshal(cards, card_fields),
            }
        elif action == "hit":
            check_cards_drawn(cards)
            new_card = hit(deck_id)
            cards.append(new_card)
            cards.sort(key=lambda x: x.owner, reverse=True)
            return get_hit_result(cards, deck)
        else:
            abort(400, message="This action is not possible...")