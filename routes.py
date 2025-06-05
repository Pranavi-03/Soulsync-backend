
from flask import request, jsonify
from app import app, db
from models import User, JournalEntry, ChatHistory
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# --- SIGNUP ROUTE ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email, username, password = data['email'], data['username'], data['password']
    
    # Check if email or username already exists
    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'error': 'Email or Username already taken'}), 400

    # Create new user with hashed password
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# --- LOGIN ROUTE ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username, password = data['username'], data['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful', 'email': user.email}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# --- JOURNAL ROUTES ---
@app.route('/journal', methods=['POST'])
def add_journal_entry():
    data = request.json
    email, entry_name, entry_text = data['email'], data['entry_name'], data['entry_text']
    user = User.query.filter_by(email=email).first()
    if user:
        new_entry = JournalEntry(user_id=user.id, entry_name=entry_name, entry_text=entry_text)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({'message': 'Journal entry added successfully'}), 201
    return jsonify({'error': 'User not found'}), 404

@app.route('/journal', methods=['GET'])
def get_journal_entries():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        entries = JournalEntry.query.filter_by(user_id=user.id).all()
        return jsonify([{'id': e.id, 'entry_name': e.entry_name, 'entry_text': e.entry_text} for e in entries]), 200
    return jsonify({'error': 'User not found'}), 404

# --- CHAT ROUTES ---
@app.route('/chat', methods=['POST'])
def store_chat_message():
    data = request.json
    email, message = data['email'], data['message']
    user = User.query.filter_by(email=email).first()
    if user:
        new_message = ChatHistory(user_id=user.id, message=message)
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'message': 'Chat message stored'}), 201
    return jsonify({'error': 'User not found'}), 404

@app.route('/chat', methods=['GET'])
def get_chat_history():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        chats = ChatHistory.query.filter(ChatHistory.user_id == user.id, ChatHistory.created_at >= thirty_days_ago).all()
        return jsonify([{'id': c.id, 'message': c.message, 'created_at': c.created_at} for c in chats]), 200
    return jsonify({'error': 'User not found'}), 404
