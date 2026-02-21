# backend/src/app.py

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, User, Analysis
from ai import AI
from config import (
    MODELS,
    MAX_TOKENS,
    DATABASE_URI,
    MAX_CONTEXT,
    RATE_LIMITS,
    ALLOWED_ORIGINS,
    CHAT_PROMPT_HEADER,
)
from auth import get_user_id
from rate_limit import limiter
from services import (
    load_user_chat_history,
    save_context_to_db,
    analyse_user_conversation,
    update_user_summary,
    user_sessions,
)
from typing import cast
from usage import check_token_limit, add_tokens, get_user_usage

"""
Endpoints:
- GET /health
- POST /api/chat
- GET /api/messages
- DELETE /api/data
- GET /api/analysis
- POST /api/analyse
- DELETE /api/user
- GET /api/usage
- GET /api/summary
"""

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

# get user tier here and select accordingly
chat_ai = AI(
    model=MODELS["sonnet"],
    max_tokens=MAX_TOKENS["chat"],
    system_prompt=CHAT_PROMPT_HEADER,  # this header is fixed
)
analysis_ai = AI(model=MODELS["haiku"], max_tokens=MAX_TOKENS["analysis"])


#### endpoints ####
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"})


@app.route("/api/chat", methods=["POST"])
@limiter.limit(RATE_LIMITS["chat"])
def post_chat():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # check tokens
    if not check_token_limit(user_id):
        return jsonify({"error": "Token limit reached"}), 429

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    message_content = data["message"].strip()
    if not message_content:
        return jsonify({"error": "Message cannot be empty"}), 400

    chat_history = load_user_chat_history(user_id)
    chat_history.append({"role": "user", "content": message_content})

    response_text, tokens = chat_ai.ask(chat_history)  # type: ignore
    if not response_text:
        response_text = "Sorry, I couldn't generate a response right now."

    chat_history.append({"role": "assistant", "content": response_text})

    add_tokens(user_id, tokens)

    if len(chat_history) > MAX_CONTEXT:
        chat_history = chat_history[-MAX_CONTEXT:]

    # save to cache and database
    user_sessions[user_id] = chat_history
    save_context_to_db(user_id, chat_history)

    return jsonify({"response": response_text})


@app.route("/api/messages", methods=["GET"])
@limiter.limit(RATE_LIMITS["read"])
def get_messages():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    chat_history = load_user_chat_history(user_id)
    return jsonify({"messages": chat_history})


@app.route("/api/data", methods=["DELETE"])
@limiter.limit(RATE_LIMITS["delete"])
def delete_data():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # clear from cache
    if user_id in user_sessions:
        user_sessions.pop(user_id, None)

    # clear from database
    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if user:
        if user.context:
            db.session.delete(user.context)
        if user.summary:
            db.session.delete(user.summary)

        Analysis.query.filter_by(user_id=user_id).delete()
        db.session.commit()

    return jsonify({"status": "User data deleted"})


@app.route("/api/analysis", methods=["GET"])
@limiter.limit(RATE_LIMITS["read"])
def get_analysis():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    analysis = cast(
        list[Analysis],
        Analysis.query.filter_by(user_id=user_id)
        .order_by(Analysis.timestamp.desc())
        .limit(30)
        .all(),
    )

    return jsonify({"analysis": [a.to_dict() for a in analysis]})


# expensive endpoint
@app.route("/api/analyse", methods=["POST"])
@limiter.limit(RATE_LIMITS["analysis"])
def post_analyse():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if not check_token_limit(user_id):
        return jsonify({"error": "Token limit reached"}), 429

    analysis, analysis_tokens = analyse_user_conversation(user_id, analysis_ai)

    if not analysis:
        return jsonify({"error": "Not enough conversation data"}), 400

    summary, summary_tokens = update_user_summary(user_id, analysis_ai)

    total_tokens = analysis_tokens + summary_tokens
    add_tokens(user_id, total_tokens)

    return jsonify({"analysis": analysis.to_dict(), "summary": summary})


@app.route("/api/user", methods=["DELETE"])
@limiter.limit(RATE_LIMITS["delete"])
def delete_user():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # clear from catch
    if user_id in user_sessions:
        user_sessions.pop(user_id, None)

    # clear from database
    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if user:
        db.session.delete(user)
        db.session.commit()

    return jsonify({"status": "User deleted"})


@app.route("/api/usage", methods=["GET"])
@limiter.limit(RATE_LIMITS["read"])
def get_usage():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    usage = get_user_usage(user_id)
    return jsonify(usage)


@app.route("/api/summary", methods=["GET"])
@limiter.limit(RATE_LIMITS["read"])
def get_summary():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if not user or not user.summary:
        return jsonify({"summary": None})

    return jsonify({"summary": user.summary.summary})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
