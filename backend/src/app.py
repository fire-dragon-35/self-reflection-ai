# backend/src/app.py

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from src.models import db, Analysis
from src.ai import AI
from src.config import (
    MODELS,
    MAX_TOKENS,
    DATABASE_URI,
    RATE_LIMITS,
    ALLOWED_ORIGINS,
    CHAT_PROMPT_HEADER,
    TOKEN_PACKAGES,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)
from src.auth import get_user_id
from src.rate_limit import limiter
from src.services import (
    load_user_chat_history,
    save_context_to_db,
    analyse_user_conversation,
    update_user_summary,
    user_sessions,
    get_or_create_user,
)
from src.usage import check_token_limit, use_tokens, get_user_usage, add_purchased_tokens
from typing import cast
import stripe

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
- POST /api/create-checkout
- POST /api/stripe-webhook
"""

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": list(ALLOWED_ORIGINS.values()),
            "methods": ["GET", "POST", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

db.init_app(app)
limiter.init_app(app)

stripe.api_key = STRIPE_SECRET_KEY

# ai instances
chat_ai = AI(
    model=MODELS["sonnet"],
    max_tokens=MAX_TOKENS["chat"],
    system_prompt=CHAT_PROMPT_HEADER,
)
analysis_ai = AI(model=MODELS["haiku"], max_tokens=MAX_TOKENS["analysis"])

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
        return jsonify({"error": "No data provided"}), 400

    message_content = data["message"].strip()
    if not message_content:
        return jsonify({"error": "No message provided"}), 400

    chat_history = load_user_chat_history(user_id)
    chat_history.append({"role": "user", "content": message_content})

    response_text, tokens = chat_ai.ask(chat_history) # type: ignore
    if not response_text:
        response_text = "Sorry, I couldn't generate a response right now."

    chat_history.append({"role": "assistant", "content": response_text})

    use_tokens(user_id, tokens)

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
    user_sessions.pop(user_id, None)

    # clear from database
    user = get_or_create_user(user_id)
    if user.context:
        db.session.delete(user.context)
    if user.summary:
        db.session.delete(user.summary)

    Analysis.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({"message": "Data cleared"})


@app.route("/api/analysis", methods=["GET"])
@limiter.limit(RATE_LIMITS["read"])
def get_analysis():
    # authentication
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
    use_tokens(user_id, total_tokens)

    return jsonify({"analysis": analysis.to_dict(), "summary": summary})


@app.route("/api/user", methods=["DELETE"])
@limiter.limit(RATE_LIMITS["delete"])
def delete_user():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    # clear from cache
    user_sessions.pop(user_id, None)

    # delete user (cascades to all data)
    user = get_or_create_user(user_id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted"})


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

    user = get_or_create_user(user_id)
    if not user.summary:
        return jsonify({"summary": None})

    return jsonify({"summary": user.summary.summary})


@app.route("/api/create-checkout", methods=["POST"])
@limiter.limit(RATE_LIMITS["read"])
def create_checkout():
    # authentication
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    package = data.get("packageType")
    
    if package not in TOKEN_PACKAGES:
        return jsonify({"error": "Invalid package"}), 400
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": TOKEN_PACKAGES[package]["price_id"],
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{ALLOWED_ORIGINS["production"]}/?success=true",
            cancel_url=f"{ALLOWED_ORIGINS["production"]}/?canceled=true",
            client_reference_id=user_id,
            metadata={
                "user_id": user_id,
                "package": package,
                "tokens": TOKEN_PACKAGES[package]["tokens"],
            }
        )
        
        return jsonify({"url": checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event( # type: ignore
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    # handle successful payment
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        tokens = int(session["metadata"]["tokens"])
        
        # add purchased tokens
        add_purchased_tokens(user_id, tokens)
        
        print(f"✨ Added {tokens} tokens to user {user_id}")
    
    return jsonify({"status": "success"})

with app.app_context():
    db.create_all()

# for local dev I guess
if __name__ == "__main__":
    app.run(debug=True, port=8000)