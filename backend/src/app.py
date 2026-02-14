# backend/src/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Analysis
from ai import AI
from config import (
    MODELS,
    MAX_TOKENS,
    DATABASE_URI,
    MAX_CONTEXT_MESSAGES,
    ANALYSIS_FREQUENCY,
    RATE_LIMITS,
    ALLOWED_ORIGINS,
    CHAT_PROMPT_HEADER
)
from auth import get_user_id
from rate_limit import limiter
from services import (
    load_user_context,
    save_context_to_db,
    analyse_user_conversation,
    clear_user_cache,
    update_user_summary,
    user_sessions,
)
from typing import cast
from dotenv import load_dotenv

"""
Endpoints:
- GET /health
- POST /api/chat
- GET /api/messages
- GET /api/analysis
- POST /api/analyse
- DELETE /api/user
- DELETE /api/data
"""

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)
db.init_app(app)
limiter.init_app(app)

chat_ai = AI(model=MODELS["chat"], max_tokens=MAX_TOKENS["chat"], system_prompt=CHAT_PROMPT_HEADER)
analysis_ai = AI(model=MODELS["analysis"], max_tokens=MAX_TOKENS["analysis"])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"})


@app.route("/api/chat", methods=["POST"])
@limiter.limit(RATE_LIMITS["chat"])
def chat():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    message_content = data["message"].strip()
    if not message_content:
        return jsonify({"error": "Message cannot be empty"}), 400

    history = load_user_context(user_id)

    history.append({"role": "user", "content": message_content})
    response_text = chat_ai.ask(history)  # type: ignore
    history.append({"role": "assistant", "content": response_text})

    if len(history) > MAX_CONTEXT_MESSAGES:
        history = history[-MAX_CONTEXT_MESSAGES:]

    # save to cache and database
    user_sessions[user_id] = history
    save_context_to_db(user_id, history)

    # analyse every N messages
    user_message_count = sum(1 for m in history if m["role"] == "user")
    if user_message_count % ANALYSIS_FREQUENCY == 0:
        analyse_user_conversation(user_id, analysis_ai)
        update_user_summary(user_id, analysis_ai)

    return jsonify({"response": response_text})


@app.route("/api/messages", methods=["GET"])
@limiter.limit(RATE_LIMITS["read"])
def get_messages():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    history = load_user_context(user_id)
    return jsonify({"messages": history})


@app.route("/api/analysis", methods=["GET"])
@limiter.limit(RATE_LIMITS["read"])
def get_analysis():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    analyses = cast(
        list[Analysis],
        Analysis.query.filter_by(user_id=user_id)
        .order_by(Analysis.timestamp.desc())
        .limit(30)
        .all(),
    )

    return jsonify({"analysis": [a.to_dict() for a in analyses]})


@app.route("/api/analyse", methods=["POST"])
@limiter.limit(RATE_LIMITS["analysis"])
def trigger_analysis():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    analysis = analyse_user_conversation(user_id, analysis_ai)

    if analysis:
        return jsonify({"message": "Analysis complete", "analysis": analysis.to_dict()})
    else:
        return jsonify({"error": "Not enough conversation data"}), 400


@app.route("/api/user", methods=["DELETE"])
@limiter.limit(RATE_LIMITS["delete"])
def delete_user():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if user:
        clear_user_cache(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"})

    return jsonify({"message": "No data found"})


@app.route("/api/data", methods=["DELETE"])
@limiter.limit(RATE_LIMITS["delete"])
def clear_data():
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if user:
        clear_user_cache(user_id)

        if user.context:
            db.session.delete(user.context)

        Analysis.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        return jsonify({"message": "User data cleared"})

    return jsonify({"message": "No data found"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
