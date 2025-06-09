from flask import Flask, request, jsonify
import requests
import random
from textblob import TextBlob
from flask_cors import CORS
import certifi
from flask_session import Session
from routes.music_routes import music_bp  # ✅ Music Blueprint
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
#CORS(app)
#CORS(app, origins="*", supports_credentials=True)
CORS(app, origins=["https://your-vercel-app.vercel.app"], supports_credentials=True)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# === Chatbot Settings ===
COHERE_API_URL = "https://api.cohere.ai/v1/chat"
HEADERS = {"Authorization": "Bearer Thg0MA42pAuX3Yc9LuqD8JAEFktzob1F0QDA2RLn"}

FALLBACK_RESPONSES = [
    "Can you tell me more about that?",
    "I'm here to listen. Please go on.",
    "That sounds important. Tell me more.",
]

MENTAL_HEALTH_TIPS = {
    "stress": [
        "Take deep breaths and try progressive muscle relaxation.",
        "Go for a short walk in nature or listen to calming music.",
        "Write down three things you're grateful for."
    ],
    "anxiety": [
        "Practice mindfulness meditation or guided breathing.",
        "Write down your thoughts and identify patterns.",
        "Try grounding techniques like focusing on your five senses."
    ],
    "depression": [
        "Reach out to a friend or journal about your emotions.",
        "Try engaging in a small activity that brings you joy.",
        "Listen to uplifting music or motivational podcasts."
    ],
}

def analyze_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"

def query_chatbot(message):
    payload = {
        "model": "command-r-plus",
        "message": message,
        "temperature": 0.7,
    }
    response = requests.post(COHERE_API_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}: {response.text}"}
    return response.json()

@app.route('/api/chatbot/', methods=['POST'])
def chatbot():
    data = request.json
    user_input = data.get("message", "").strip().lower()
    response_text = None

    if user_input in ["hi", "hello", "hey"]:
        response_text = "Hello! How can I support you today? 😊"

    sentiment = analyze_sentiment(user_input)
    if sentiment == "negative":
        for emotion, tips in MENTAL_HEALTH_TIPS.items():
            if emotion in user_input:
                response_text = f"I sense some {emotion}. Here’s a suggestion: {random.choice(tips)}"
                break

    if response_text is None:
        result = query_chatbot(user_input)
        response_text = result.get("text", random.choice(FALLBACK_RESPONSES)) if "error" not in result else f"SoulSync Error: {result['error']}"

    return jsonify({"response": response_text})

# ✅ Register Music Blueprint
app.register_blueprint(music_bp)

if __name__ == '__main__':
    app.run(debug=True)
