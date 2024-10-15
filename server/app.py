from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Pizza Restaurant API</h1>'

@app.route('/restaurants', methods=['GET', 'POST'])
def handle_restaurants():
    if request.method == 'POST':
        data = request.json
        try:
            new_restaurant = Restaurant(
                name=data['name'],
                address=data['address']
            )
            db.session.add(new_restaurant)
            db.session.commit()
            return jsonify({
                "id": new_restaurant.id,
                "name": new_restaurant.name,
                "address": new_restaurant.address
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        restaurants = Restaurant.query.all()
        return jsonify([{
            "id": r.id,
            "name": r.name,
            "address": r.address
        } for r in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def get_or_delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        if request.method == 'DELETE':
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [{
                "id": rp.id,
                "pizza": {
                    "id": rp.pizza.id,
                    "ingredients": rp.pizza.ingredients,
                    "name": rp.pizza.name
                },
                "pizza_id": rp.pizza_id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id
            } for rp in restaurant.restaurant_pizzas]
        })
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "ingredients": p.ingredients
    } for p in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.json
    try:
        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify({
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,
            "restaurant_id": restaurant_pizza.restaurant_id
        }), 201
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400
    except Exception as e:
        return jsonify({"errors": ["validation errors"]}), 400

@app.route('/restaurant_pizzas', methods=['GET'])
def get_restaurant_pizzas():
    restaurant_pizzas = RestaurantPizza.query.all()
    return jsonify([{
        "id": rp.id,
        "price": rp.price,
        "pizza_id": rp.pizza_id,
        "restaurant_id": rp.restaurant_id
    } for rp in restaurant_pizzas])

@app.route('/restaurant_pizzas/<int:id>', methods=['DELETE'])
def delete_restaurant_pizza(id):
    restaurant_pizza = RestaurantPizza.query.get(id)
    if restaurant_pizza:
        db.session.delete(restaurant_pizza)
        db.session.commit()
        return '', 204  
    else:
        return jsonify({"error": "Restaurant-Pizza relationship not found"}), 404

if __name__ == '__main__':
    app.run(port=5555, debug=True)
