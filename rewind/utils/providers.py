"""Model provider types."""
import enum

class ProviderType(enum.Enum):
    """Different model provider"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    QWEN = "qwen"
