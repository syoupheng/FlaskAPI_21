from flask import Flask
from flask_restful import Api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@server/db_name'
api = Api(app)
from database import db
db.init_app(app)

from resources import DeckResource, GameResource        
api.add_resource(DeckResource, "/deck/new")
api.add_resource(GameResource,"/deck/<int:deck_id>/<string:action>")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)