"""numberic data calculation"""
from typing import List, Dict, Tuple
from rewind.data_process.loading_data import load_json
from rewind.data_process.update_data import update_data
from rewind.utils.language_utils import (chinese_dominant, count_code_block_languages,
                                        REFUSE_WORDS_LIST)
from rewind.data_process.style_data import polite_count, emoji_count
from rewind.utils.data_utils import iterate_fragments, iterate_fragments_with_model
from rewind.data_process.time_data import chat_frequency_distribution, chat_themost

def session_count_stats(data_list: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Get raw data session count
    """
    return {"session_count": len(data_list)}

def prefer_model_count(data_list: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Given a list of dictionaries containing model statistics,
    return the dictionary with the highest 'preference_score'.
    """
    model_counts = {}

    for session in data_list:

        interaction = session.get("longest_interaction_list", [])

        for _, record in enumerate(interaction):
            fragments = record.get("message", {}).get("fragments", [])
            if len(fragments) == 0:
                break
            for fragment in fragments:
                interact_type = fragment.get("type", "")
                if interact_type in ('RESPONSE'):
                    model_type = record.get("message", {}).get("model", "unknown")
                    if model_type not in model_counts:
                        model_counts[model_type] = 0
                    model_counts[model_type] += 1

    return model_counts


def count_chars(data_list: List[Dict[str, any]]) -> Dict[str, int]:
    """
    Count the total number of characters in the 'fragments' of each record's message.
    """
    char_dict = {}

    for content, interaction_type, model_type in iterate_fragments_with_model(data_list):
        full_key = f"{model_type}_{interaction_type}"

        if full_key not in char_dict:
            char_dict[full_key] = 0
        char_count = len(content)
        char_dict[full_key] += char_count

    return char_dict

def language_dominant_count(data_list: List[Dict[str, any]]) -> \
    Tuple[Dict[str, int], Dict[str, int]]:
    """
    Count the number of Chinese dominant messages in the 'fragments' of each record's message.
    """
    chinese_dominant_dict = {}
    else_dominant_dict = {}

    for content, interaction_type, model_type in iterate_fragments_with_model(data_list):
        full_key = f"{model_type}_{interaction_type}"

        if full_key not in chinese_dominant_dict:
            chinese_dominant_dict[full_key] = 0
        if full_key not in else_dominant_dict:
            else_dominant_dict[full_key] = 0

        if chinese_dominant(content):
            chinese_dominant_dict[full_key] += 1
        else:
            else_dominant_dict[full_key] += 1

    return chinese_dominant_dict, else_dominant_dict

def code_language_count(data_list: List[Dict[str, any]]) -> Dict[str, int]:
    """
    Count the number of code blocks by programming language
    in the 'fragments' of each record's message.
    """
    total_language_count = {}

    for content, interaction_type in iterate_fragments(data_list):
        if interaction_type == "REQUEST":
            continue
        language_count = count_code_block_languages(content)

        for lang, count in language_count.items():
            if lang not in total_language_count:
                total_language_count[lang] = 0
            total_language_count[lang] += count

    return total_language_count

def ai_refuse_count(data_list: List[Dict[str, any]]) -> int:
    """
    Count the number of AI refusal messages in the 'fragments' of each record's message.
    """
    refuse_count = 0

    for content, interaction_type in iterate_fragments(data_list):
        if interaction_type == "RESPONSE" and \
            any(refuse_word in content for refuse_word in REFUSE_WORDS_LIST) and \
            len(content) < 50:
            refuse_count += 1

    return refuse_count


def main():
    """main function for numberic stats"""

    data = load_json('data/conversations.json')
    print("Session Count Stats:", session_count_stats(data))

    data = update_data(data)

    print("Updated Data List Length:", len(data))

    prefer_model_stats = prefer_model_count(data)
    print("Prefer Model Stats:", prefer_model_stats)

    total_char_count = count_chars(data)
    print("Total Character Count:", total_char_count)

    chinese_dominant_stats = language_dominant_count(data)
    print("Chinese Dominant Count Stats:", chinese_dominant_stats)

    code_lang_count = code_language_count(data)
    print("Code Language Count Stats:", code_lang_count)

    chat_refuse_stats = ai_refuse_count(data)
    print("AI Refuse Count Stats:", chat_refuse_stats)

    polite_stats = polite_count(data)
    print("Polite Count Stats:", polite_stats)

    emoji_stats = emoji_count(data)
    print("Emoji Count Stats:", emoji_stats)

    chat_freq_stats = chat_frequency_distribution(data)
    print("Chat Frequency Distribution Stats:", chat_freq_stats)

    chat_themost_stats = chat_themost(data)
    print("Chat The Most Stats:", chat_themost_stats["max_interaction_count"])

if __name__ == "__main__":
    main()
