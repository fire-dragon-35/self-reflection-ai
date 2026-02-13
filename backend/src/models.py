# backend/src/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from typing import TypedDict, cast
import os
import json


# types
class BigFiveDict(TypedDict):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float


class AttachmentStyleDict(TypedDict):
    anxiety_score: float
    avoidance_score: float
    style: str


class AnalysisDict(TypedDict):
    id: int
    big_five_personality: BigFiveDict | None
    attachment_style: AttachmentStyleDict | None
    timestamp: str


db = SQLAlchemy()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)


def encrypt(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()


def decrypt(data: str) -> str:
    return cipher.decrypt(data.encode()).decode()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # relationships
    context = db.relationship(
        "Context", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    analyses = db.relationship(
        "Analysis", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )


class Context(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(100), db.ForeignKey("user.user_id"), nullable=False, unique=True
    )
    messages_encrypted = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def messages(self):
        decrypted = decrypt(self.messages_encrypted)
        return json.loads(decrypted)

    @messages.setter
    def messages(self, value: list[dict[str, str]]) -> None:
        json_str = json.dumps(value)
        self.messages_encrypted = encrypt(json_str)


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(100), db.ForeignKey("user.user_id"), nullable=False, index=True
    )
    big_five_personality_encrypted = db.Column(db.Text)
    attachment_style_encrypted = db.Column(db.Text)
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )

    @property
    def big_five_personality(self) -> BigFiveDict | None:
        if not self.big_five_personality_encrypted:
            return None
        decrypted = decrypt(self.big_five_personality_encrypted)
        return cast(BigFiveDict, json.loads(decrypted))

    @big_five_personality.setter
    def big_five_personality(self, value: BigFiveDict | None) -> None:
        if value is None:
            self.big_five_personality_encrypted = None
        else:
            json_str = json.dumps(value)
            self.big_five_personality_encrypted = encrypt(json_str)

    @property
    def attachment_style(self) -> AttachmentStyleDict | None:
        if not self.attachment_style_encrypted:
            return None
        decrypted = decrypt(self.attachment_style_encrypted)
        return cast(AttachmentStyleDict, json.loads(decrypted))

    @attachment_style.setter
    def attachment_style(self, value: AttachmentStyleDict | None) -> None:
        if value is None:
            self.attachment_style_encrypted = None
        else:
            json_str = json.dumps(value)
            self.attachment_style_encrypted = encrypt(json_str)

    def to_dict(self) -> AnalysisDict:
        return {
            "id": self.id,
            "big_five_personality": self.big_five_personality,
            "attachment_style": self.attachment_style,
            "timestamp": self.timestamp.isoformat(),
        }
