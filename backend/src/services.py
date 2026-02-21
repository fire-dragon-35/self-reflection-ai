# backend/src/services.py

from models import db, User, Context, Analysis, Summary
from datetime import datetime, timezone
from ai import AI
from config import (
    BIG_FIVE_PROMPT_HEADER,
    ATTACHMENT_STYLE_PROMPT_HEADER,
    SUMMARY_PROMPT_HEADER,
    MIN_ANALYSIS_CONTEXT,
    MAX_CONTEXT
)
import json
from typing import cast

Chat = list[dict[str, str]]

# cache
user_sessions: dict[str, Chat] = {}

def get_or_create_user(user_id: str) -> User:
    user = cast(User | None, User.query.filter_by(user_id=user_id).first())
    if not user:
        user = User(user_id=user_id)  # type: ignore
        db.session.add(user)
        db.session.commit()
    return user


def load_user_chat_history(user_id: str) -> Chat:
    # check cache
    if user_id in user_sessions:
        return user_sessions[user_id]

    user = get_or_create_user(user_id)
    chat_history: Chat = []
    if user.context:
        chat_history = user.context.messages.copy()

    user_sessions[user_id] = chat_history
    return chat_history


def save_context_to_db(user_id: str, chat_history: Chat) -> None:
    user = get_or_create_user(user_id)
    
    # update cache
    user_sessions[user_id] = chat_history

    if user.context:
        user.context.messages = chat_history  # type: ignore
        user.context.updated_at = datetime.now(timezone.utc)  # type: ignore
    else:
        context = Context(user_id=user_id, messages=chat_history)  # type: ignore
        db.session.add(context)

    db.session.commit()


def _clean_json_response(text: str) -> str:
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}")
    return text[start : end + 1] if start != -1 and end != -1 else text


def analyse_user_conversation(
    user_id: str, analysis_ai: AI
) -> tuple[Analysis | None, int]:
    
    chat_history = load_user_chat_history(user_id)

    if len(chat_history) < MIN_ANALYSIS_CONTEXT:
        return None, 0

    # trim
    context_window = chat_history[-MAX_CONTEXT:]

    user = get_or_create_user(user_id)
    existing_summary = ""
    if user.summary:
        existing_summary = (
            f"\n\nPrevious conversation summary:\n{user.summary.summary}\n\n"
        )

    recent_conversation = "\n\n".join(
        [f"{m['role'].title()}: {m['content']}" for m in context_window]
    )

    big_five_prompt = (
        BIG_FIVE_PROMPT_HEADER
        + existing_summary
        + "Recent conversation:\n"
        + recent_conversation
    )
    attachment_prompt = (
        ATTACHMENT_STYLE_PROMPT_HEADER
        + existing_summary
        + "Recent conversation:\n"
        + recent_conversation
    )

    total_tokens = 0

    try:
        # big 5 analysis
        big_five_text, tokens = analysis_ai.ask(
            [{"role": "user", "content": big_five_prompt}]
        )
        big_five_text = _clean_json_response(big_five_text)
        total_tokens += tokens

        # attachment analysis
        attachment_text, tokens = analysis_ai.ask(
            [{"role": "user", "content": attachment_prompt}]
        )
        attachment_text = _clean_json_response(attachment_text)
        total_tokens += tokens

        big_five_data = json.loads(big_five_text)
        attachment_data = json.loads(attachment_text)

        analysis = Analysis(
            user_id=user_id, # type: ignore
            big_five_personality=big_five_data, # type: ignore
            attachment_style=attachment_data, # type: ignore
        )
        db.session.add(analysis)
        db.session.commit()

        print(f"✨ Analysis using {len(context_window)} messages (out of {len(chat_history)} total), {total_tokens} tokens")

        return analysis, total_tokens

    except Exception:
        return None, 0


def update_user_summary(user_id: str, analysis_ai: AI) -> tuple[str | None, int]:
    user = get_or_create_user(user_id)
    chat_history = load_user_chat_history(user_id)

    if len(chat_history) < MIN_ANALYSIS_CONTEXT:
        return None, 0

    context_window = chat_history[-MAX_CONTEXT:]

    existing_summary = ""
    if user.summary:
        existing_summary = user.summary.summary

    recent_conversation = "\n\n".join(
        [f"{m['role'].title()}: {m['content']}" for m in context_window]
    )

    prompt = (
        SUMMARY_PROMPT_HEADER
        + f"\n\nPrevious summary:\n{existing_summary if existing_summary else 'None. This is the first summary.'}\n\n"
        + f"Recent conversations:\n{recent_conversation}"
    )

    new_summary, tokens = analysis_ai.ask([{"role": "user", "content": prompt}])

    if user.summary:
        user.summary.summary = new_summary  # type: ignore
        user.summary.updated_at = datetime.now(timezone.utc)  # type: ignore
    else:
        summary = Summary(user_id=user_id, summary=new_summary)  # type: ignore
        db.session.add(summary)

    db.session.commit()

    print(f"✨ Summary using {len(context_window)} messages (out of {len(chat_history)} total), {tokens} tokens")

    return new_summary, tokens