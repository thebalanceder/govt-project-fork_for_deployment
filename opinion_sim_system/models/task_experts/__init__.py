"""Task expert adapters for Semantic Frontend v2."""

from .acceptance_expert import AcceptanceExpert
from .base import InputCase, TaskExpert, TaskExpertInput, TaskExpertOutput
from .conflict_expert import ConflictExpert
from .emotion_expert import EmotionExpert
from .frame_expert import FrameExpert
from .sentiment_expert import SentimentExpert
from .topic_expert import TopicExpert

# Backward-compatible aliases for previous naming.
StanceExpert = AcceptanceExpert
RiskExpert = ConflictExpert
ValueFrameExpert = FrameExpert

__all__ = [
    "AcceptanceExpert",
    "ConflictExpert",
    "EmotionExpert",
    "FrameExpert",
    "InputCase",
    "RiskExpert",
    "SentimentExpert",
    "StanceExpert",
    "TaskExpert",
    "TaskExpertInput",
    "TaskExpertOutput",
    "TopicExpert",
    "ValueFrameExpert",
]
