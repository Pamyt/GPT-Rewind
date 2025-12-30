"""basic api for data overview"""
from typing import List, Dict, Any
from rewind.data_process import (
    session_count_stats,
    prefer_model_count,
    count_chars,
    language_dominant_count,
    code_language_count,
    load_json,
    update_data,
    ai_refuse_count
)
from rewind.utils.providers import ProviderType
from rewind.utils.cache_utils import get_cache_manager

cache_manager = get_cache_manager()


def session_count(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> Dict[str, Any]:
    """get session count stats from json file"""
    data = load_json(json_path)
    data = update_data(data, provider_type)

    return session_count_stats(data)

def most_used_models(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> List[Dict[str, Any]]:
    """how many times each model is used"""
    data = load_json(json_path)
    data = update_data(data, provider_type)

    model_counts = prefer_model_count(data)

    answer_list = []

    for model, count in model_counts.items():
        answer_list.append({"model": model, "usage": count})

    return answer_list


def total_characters(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> List[Dict[str, Any]]:
    """how many characters each model has generated or user has inputted"""
    data = load_json(json_path)
    data = update_data(data, provider_type)

    char_counts = count_chars(data)

    answer_list = []

    for key, count in char_counts.items():
        if count > 0:
            answer_list.append({"model_type": key, "counts": count})

    return answer_list


def most_used_language(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> List[Dict[str, Any]]:
    """which language is used the most"""
    # Try to get from cache
    cached_result = cache_manager.get(json_path, f"most_used_language_{provider_type.value}")
    if cached_result is not None:
        return cached_result

    data = load_json(json_path)
    data = update_data(data, provider_type)

    natural_language_stats, _ = language_dominant_count(data)

    answer_list = []

    # Process natural languages
    # natural_language_stats structure: {"Model_Type": {"en": 10, "zh-cn": 5}}
    for model_type_key, lang_counts in natural_language_stats.items():
        for lang_code, count in lang_counts.items():
            if count > 0:
                answer_list.append({
                    "model_type": model_type_key,
                    "counts": count,
                    "type": "natural",
                    "language": lang_code
                })

    code_counts = code_language_count(data)
    for key, count in code_counts.items():
        answer_list.append({"model_type": "all", "counts": count, \
            "type": "code", "language": key})

    # Save to cache
    cache_manager.set(json_path, f"most_used_language_{provider_type.value}", answer_list)

    return answer_list

def refuse_counts(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) -> int:
    """how many refuse responses are there"""
    data = load_json(json_path)
    data = update_data(data, provider_type)

    return ai_refuse_count(data)

def main():
    """base api testing"""
    data_path = "data/qwen_conversations.json"
    print(session_count(data_path, ProviderType.QWEN))
    print(most_used_models(data_path, ProviderType.QWEN))
    print(total_characters(data_path, ProviderType.QWEN))
    print(most_used_language(data_path, ProviderType.QWEN))
    print(refuse_counts(data_path, ProviderType.QWEN))

if __name__ == "__main__":
    main()
