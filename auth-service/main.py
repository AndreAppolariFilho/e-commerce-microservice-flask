import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APPLICATION_SECRET_KEY", "SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL", 'sqlite:///db/users.db')
app.config["JWT_SECRET_KEY"] = os.environ.get("APPLICATION_JWT_SECRET_KEY", 'your_jwt_secret_key')
db = SQLAlchemy(app)
# JWT Initialization
jwt = JWTManager(app)

"""
Models
"""


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_admin = db.Column(db.Boolean, default=False)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_admin": self.is_admin
        }


"""
Views
"""


@app.route('/register', methods=["POST"])
def register():
    if request.method == "POST":
        data = request.get_json()
        if db.session.execute(db.select(User).where(User.username == data["username"])).scalar():
            return {
                "msg": "User already exists"
            }, 400
        user = User()
        user.username = data["username"]
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize()), 200


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        user = db.session.execute(db.select(User).where(User.username == data["username"])).scalar()
        if not user:
            return {
                "msg": "User not found"
            }, 400
        if not user.check_password(data["password"]):
            return {
                "msg": "Wrong password"
            }, 400
        access_token = create_access_token(identity=user.username)
        return jsonify({"access_token": access_token})


@app.route("/validate", methods=["POST"])
@jwt_required()
def validate():
    if request.method == "POST":
        username = get_jwt_identity()
        user = db.session.execute(db.select(User).where(User.username == username)).scalar()
        if not user:
            return jsonify({
                "error": "User doesn't exist"
            }), 404
        return jsonify(user.serialize()), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("port", "5001"))
