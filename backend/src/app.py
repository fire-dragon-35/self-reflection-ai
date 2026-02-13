# backend/src/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.src.ai import AI
from config import MODELS, MAX_TOKENS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


# AI instances
chat_ai = AI(model=MODELS["chat"], max_tokens=MAX_TOKENS["chat"])
analysis_ai = AI(model=MODELS["analysis"], max_tokens=MAX_TOKENS["analysis"])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message"}), 400

    message = data["message"]

    response = chat_ai.ask([{"role": "user", "content": message}])

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
