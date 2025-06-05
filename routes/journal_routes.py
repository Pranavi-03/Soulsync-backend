from flask import Blueprint, request, jsonify
from database import db, JournalEntry

journal_bp = Blueprint('journal_routes', __name__)

@journal_bp.route('/add-journal', methods=['POST'])
def add_journal():
    data = request.json
    new_entry = JournalEntry(user_id=data['user_id'], title=data['title'], content=data['content'])
    
    db.session.add(new_entry)
    db.session.commit()
    
    return jsonify({"message": "Journal entry saved!"}), 201

@journal_bp.route('/get-journals/<int:user_id>', methods=['GET'])
def get_journals(user_id):
    entries = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.created_at.desc()).all()
    return jsonify([{"id": e.id, "title": e.title, "created_at": e.created_at} for e in entries])
