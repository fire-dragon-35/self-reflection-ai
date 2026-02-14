# backend/src/services.py

from models import db, User, Context, Analysis
from datetime import datetime, timezone
from typing import cast
from ai import AI
from config import (
    BIG_FIVE_PROMPT_HEADER,
    ATTACHMENT_STYLE_PROMPT_HEADER,
    SUMMARY_PROMPT_HEADER,
)
import json

"""
Services here:
- load_user_context
- save_context_to_db
- analyse_user_conversation
- clear_user_cache
"""

# define types
Messages = list[dict[str, str]]
user_sessions: dict[str, Messages] = {}


def _get_or_create_user(user_id: str) -> User:
    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if not user:
        user = User(user_id=user_id)  # type: ignore
        db.session.add(user)
        db.session.commit()
    return user


def load_user_context(user_id: str) -> Messages:
    if user_id in user_sessions:
        return user_sessions[user_id]

    user = _get_or_create_user(user_id)
    history: Messages = []
    if user.context:
        history = user.context.messages.copy()

    user_sessions[user_id] = history
    return history


def save_context_to_db(user_id: str, history: Messages) -> None:
    user = _get_or_create_user(user_id)

    if user.context:
        user.context.messages = history  # type: ignore
        user.context.updated_at = datetime.now(timezone.utc)  # type: ignore
    else:
        context = Context(user_id=user_id)  # type: ignore
        context.messages = history
        db.session.add(context)

    db.session.commit()


def _clean(text: str) -> str:
    # clean json response from code block formatting if present
    return text.replace("```json", "").replace("```", "").strip()


def analyse_user_conversation(user_id: str, analysis_ai: AI) -> Analysis | None:
    history = load_user_context(user_id)

    if len(history) < 6:
        return None

    conversation = "\n\n".join(
        [f"{m['role'].title()}: {m['content']}" for m in history]
    )

    big_five_prompt = BIG_FIVE_PROMPT_HEADER + "\n\nConversation:\n" + conversation
    attachment_prompt = (
        ATTACHMENT_STYLE_PROMPT_HEADER + "\n\nConversation:\n" + conversation
    )

    try:
        big_five_text = _clean(
            analysis_ai.ask([{"role": "user", "content": big_five_prompt}])
        )
        attachment_text = _clean(
            analysis_ai.ask([{"role": "user", "content": attachment_prompt}])
        )
        big_five_data = json.loads(big_five_text)
        attachment_data = json.loads(attachment_text)

        analysis = Analysis(user_id=user_id)  # type: ignore
        analysis.big_five_personality = big_five_data
        analysis.attachment_style = attachment_data

        db.session.add(analysis)
        db.session.commit()

        return analysis

    except Exception as e:
        print(f"Analysis error: {e}")
        return None


def clear_user_cache(user_id: str) -> None:
    user_sessions.pop(user_id, None)


def update_user_summary(user_id: str, analysis_ai: AI) -> None:
    user = _get_or_create_user(user_id)

    recent_history = load_user_context(user_id)

    existing_summary = ""
    if user.summary:
        existing_summary = user.summary.summary

    conversation = "\n\n".join(
        [f"{m['role'].title()}: {m['content']}" for m in recent_history]
    )

    prompt = (
        SUMMARY_PROMPT_HEADER
        + f"\n\nPrevious summary:\n{existing_summary if existing_summary else 'None - this is the first summary.'}\n\n"
        + f"Recent conversations:\n{conversation}"
    )

    new_summary = analysis_ai.ask([{"role": "user", "content": prompt}])  # type: ignore

    if user.summary:
        user.summary.summary = new_summary  # type: ignore
        user.summary.updated_at = datetime.now(timezone.utc)  # type: ignore
    else:
        summary = Summary(user_id=user_id)  # type: ignore
        summary.summary = new_summary  # type: ignore
        db.session.add(summary)  # type: ignore

    db.session.commit()
