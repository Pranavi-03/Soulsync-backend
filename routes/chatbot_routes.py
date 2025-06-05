from flask import Blueprint, request, jsonify
from textblob import TextBlob
import random
import requests

chatbot_bp = Blueprint("chatbot", __name__)

COHERE_API_URL = "https://api.cohere.ai/v1/chat"
HEADERS = {"Authorization": "Bearer YOUR_COHERE_API_KEY"}

MENTAL_HEALTH_TIPS = {
    "stress": ["Take deep breaths", "Go for a walk", "Listen to calming music"],
    "anxiety": ["Try mindfulness exercises", "Practice grounding techniques"],
    "depression": ["Journal your thoughts", "Engage in a small activity"],
}

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    return "positive" if polarity > 0.2 else "negative" if polarity < -0.2 else "neutral"

@chatbot_bp.route("/", methods=["POST"])
def chatbot_response():
    user_input = request.json.get("message")
    sentiment = analyze_sentiment(user_input)

    response_text = None
    if sentiment == "negative":
        for emotion, tips in MENTAL_HEALTH_TIPS.items():
            if emotion in user_input:
                response_text = f"I sense {emotion}. Here's a tip: {random.choice(tips)}"
                break

    if not response_text:
        payload = {"model": "command-r-plus", "message": user_input, "temperature": 0.7}
        response = requests.post(COHERE_API_URL, headers=HEADERS, json=payload)
        response_text = response.json().get("text", "I'm here to help.") if response.status_code == 200 else "Chatbot unavailable."

    return jsonify({"response": response_text})
