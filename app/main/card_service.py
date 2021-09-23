import random

from models import Card, Deck, card_fields
from flask_restful import abort, marshal
from deck_service import delete_deck
from database import db

def shuffle_cards(cards, deck_id):
    deck = Deck.query.filter_by(id=deck_id).first()
    if not deck:
        abort(404, message="There is no deck with this id...")
    if not deck.shuffled:
        deck.shuffled = True
        db.session.commit()
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

def check_cards_drawn(cards):
    if not cards:
            abort(400, message="You need to draw cards before choosing to stand or hit...")

def get_hit_result(cards, deck):
    score = calculateScore(cards)
    if score["Player"] == 21:
        delete_deck(deck)
        msg = "You have a 21 ! You won !"
        result = cards
    elif score["Player"] > 21:
        delete_deck(deck)
        msg = "You busted ! Your score went over 21 ! Better luck next time..."
        result = cards
    else:
        result = []
        for card in cards:
            if card.face_up:
                result.append(card)
        result.sort(key=lambda x: x.owner, reverse=True)
        msg = "You successfully drew a card from the deck"
    return {
        "msg": msg,
        "Cards":marshal(result, card_fields),
    } 

def get_draw_result(deck, score):
    cards = draw(deck.id)
    if score["Player"] == 21:
        delete_deck(deck)
        result = cards[:4]
        if score["Dealer"] != 21:
            msg = "You have a natural 21 ! You won !"
        else:
            msg = "This is a tie with the dealer!"
    elif score["Dealer"] == 21:
        msg = "The dealer has a natural 21 ! You lost...Better luck next time !"
        result = cards[:4]
        delete_deck(deck)
    else:
        msg = "You drew 2 cards face up and the dealer drew one card face up and one card face down. Now you need to choose between ask for another card (hit) or not (stand)"
        result = cards[:3]
    return {
        "msg":msg,
        "Cards":marshal(result, card_fields)
    }