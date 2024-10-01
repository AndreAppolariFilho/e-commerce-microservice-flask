import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APPLICATION_SECRET_KEY", "SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL", 'sqlite:///db/shopping.db')
app.config["JWT_SECRET_KEY"] = os.environ.get("APPLICATION_JWT_SECRET_KEY", 'your_jwt_secret_key')
db = SQLAlchemy(app)
# JWT Initialization
jwt = JWTManager(app)
auth_service_base_url = os.environ.get("auth_service_base_url", "http://auth_service:5001")
products_service_base_url = os.environ.get("products_service_base_url", "http://products_service:5002")

"""
Models
"""


class ShoppingCart(db.Model):
    __tablename__ = "shoppingcarts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    shopping_items = db.relationship("ShoppingCartItem", backref="shoppingcarts", lazy="select")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "shopping_items": self.shopping_items
        }


class ShoppingCartItem(db.Model):
    __tablename__ = "shoppingcartitems"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    shopping_cart_id = db.Column(db.Integer, db.ForeignKey(ShoppingCart.id, ondelete="CASCADE"), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "price": self.price,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_id": self.product_id
        }

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("port", "5003"))
