"""Style analysis for user side and ai side"""
from typing import List, Dict
import emoji
from rewind.utils.language_utils import POLITE_WORDS_LIST, IMPOLITE_WORDS_LIST
from rewind.utils.data_utils import iterate_fragments


def polite_count(data_list: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    Count the number of polite and impolite words in the 'fragments' of each record's message.
    Returns a list of dictionaries with format: [{"word":"您","counts":"10"}, ...]
    """
    polite_stats = {}

    for content, interaction_type in iterate_fragments(data_list):
        if interaction_type == "REQUEST":
            _count_polite_words(content, polite_stats)
            _count_impolite_words(content, polite_stats)

    # Convert dictionary to list of dictionaries format
    result = [{"word": word, "counts": str(count)} for word, count in polite_stats.items()]
    return result


def _count_polite_words(content: str, polite_stats: Dict[str, int]) -> None:
    """Count polite words in content and update stats."""
    for polite_word in POLITE_WORDS_LIST:
        if polite_word in content:
            polite_stats[polite_word] = polite_stats.get(polite_word, 0) + 1


def _count_impolite_words(content: str, polite_stats: Dict[str, int]) -> None:
    """Count impolite words in content and update stats."""
    for impolite_word in IMPOLITE_WORDS_LIST:
        if impolite_word in content:
            polite_stats[impolite_word] = polite_stats.get(impolite_word, 0) + 1


def emoji_count(data_list: List[Dict[str, any]]) -> Dict[any, int]:
    """
    Count the number of emojis in the 'fragments' of each record's message.
    """
    emoji_stats = {}

    for content, interaction_type in iterate_fragments(data_list):
        if interaction_type != "REQUEST":
            _count_emojis(content, emoji_stats)
    result=[{"emoji": emo, "counts": str(count)} for emo, count in emoji_stats.items()]
    return result


def _count_emojis(content: str, emoji_stats: Dict[str, int]) -> None:
    """Count emojis in content and update stats."""
    for char in content:
        if char in emoji.EMOJI_DATA:
            emoji_stats[char] = emoji_stats.get(char, 0) + 1
