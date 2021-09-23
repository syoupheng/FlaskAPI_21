## FlaskRESTful API : 21 Card game

# I) Introduction

For this project I created a small API with Flask-restful which allows the user to play a very simplified version of blackjack.

Rules: In this game you are going to play with the dealer. Each of you will draw cards from a 52-cards deck and the goal is to get a score of 21 or higher than the dealer's. The value of the cards from 2 to 10 is given by their number except for the as which has a value of 1 or 11 (your choice). The face cards (jack, queen and king) have a value of 10.

In order to start a game you need to create a deck with this POST request: `/deck/new`

You will then receive a message containing the id of your deck. You will need this id to play with this deck. After creating the deck you need to shuffle it with this POST request: `/deck/<deck_id>/shuffle`

You should now receive a success message which means that you can draw your first cards with this PUT request: `/deck/<deck_id>/draw`

With this request you and the dealer will draw 2 cards and the dealer will have one card face down. Then you will be asked to "hit" or "stand": PUT method `/deck/<deck_id>/hit or stand`
"hit" means drawing another card in order to get a score closer to 21 and "stand" means not drawing new cards. When you choose stand your score will be compared with the dealer's and the winner will be decided. 

# II) Setting up the environnement

After cloning this project you need to create a virtual environnement (venv) by using this command:
`python3 -m venv venv
source venv/bin/activate`

The virtual environnement allows you to install packages only for this project. Now that the venv is activated you can install the packages required by this project with: `python3 -m pip install -r requirements.txt`

# III) Database configuration

For this project I used a mySQL database with SQLAlchemy as an abstraction layer but you should be able to use other databases such as postgreSQL or SQLite, you just have to put the URI of your database in blackjack.py on this line:
`app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@server/db_name'`
You will also need to create an empty database before starting the server. SQLAlchemy will then automatically create the tables.

# IV) How to start the API

In order to start the API you only need to execute the blackjack.py with this command: `python3 blackjack.py`. Now that the API server is running you can send requests (see introduction) by typing this URL: `localhost:<port_number>/`. The port number should be displayed in your terminal when starting the server (the default port number should be 5000). It is recommended to use a tool such as Postman which allows you to specify the request method.