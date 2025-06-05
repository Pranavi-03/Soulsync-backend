from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User

user_bp = Blueprint('user_routes', __name__)

@user_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
        return jsonify({"message": "Email or Username already exists"}), 400
    
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(email=data['email'], username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"message": "Invalid credentials"}), 401
    
    return jsonify({"message": "Login successful", "user_id": user.id}), 200
