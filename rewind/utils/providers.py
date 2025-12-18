"""Model provider types."""
import enum

class ProviderType(enum.Enum):
    """Different model provider"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
