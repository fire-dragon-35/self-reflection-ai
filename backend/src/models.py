# backend/src/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from typing import TypedDict, cast
from config import ENCRYPTION_KEY
import json


# data types
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

if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY is not set in environment variables")
cipher = Fernet(ENCRYPTION_KEY.encode())


def encrypt(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()


def decrypt(data: str) -> str:
    return cipher.decrypt(data.encode()).decode()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # token tracking
    tier = db.Column(db.String(20), default="free", nullable=False)
    tokens_used = db.Column(db.Integer, default=0, nullable=False)
    tokens_reset_date = db.Column(
        db.Date, default=lambda: datetime.now(timezone.utc).date(), nullable=False
    )

    # Relationships
    context = db.relationship(
        "Context", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    analyses = db.relationship(
        "Analysis", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    summary = db.relationship(
        "Summary", backref="user", uselist=False, cascade="all, delete-orphan"
    )


class Context(db.Model):
    __tablename__ = "context"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(100), db.ForeignKey("user.user_id"), nullable=False, unique=True
    )
    messages_encrypted = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def messages(self) -> list[dict[str, str]]:
        decrypted = decrypt(self.messages_encrypted)
        return json.loads(decrypted)

    @messages.setter
    def messages(self, value: list[dict[str, str]]) -> None:
        json_str = json.dumps(value)
        self.messages_encrypted = encrypt(json_str)


class Analysis(db.Model):
    __tablename__ = "analysis"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(100), db.ForeignKey("user.user_id"), nullable=False, index=True
    )
    big_five_personality_encrypted = db.Column(db.Text)
    attachment_style_encrypted = db.Column(db.Text)
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
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


class Summary(db.Model):
    __tablename__ = "summary"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(100), db.ForeignKey("user.user_id"), nullable=False, unique=True
    )
    summary_encrypted = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def summary(self) -> str:
        return decrypt(self.summary_encrypted)

    @summary.setter
    def summary(self, value: str) -> None:
        self.summary_encrypted = encrypt(value)
