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


def session_count(json_path: str) -> Dict[str, Any]:
    """get session count stats from json file"""
    data = load_json(json_path)
    data = update_data(data)

    return session_count_stats(data)

def most_used_models(json_path: str) -> List[Dict[str, Any]]:
    """how many times each model is used"""
    data = load_json(json_path)
    data = update_data(data)

    model_counts = prefer_model_count(data)

    answer_list = []

    for model, count in model_counts.items():
        answer_list.append({"model": model, "usage": count})

    return answer_list


def total_characters(json_path: str) -> List[Dict[str, Any]]:
    """how many characters each model has generated or user has inputted"""
    data = load_json(json_path)
    data = update_data(data)

    char_counts = count_chars(data)

    answer_list = []

    for key, count in char_counts.items():
        if count > 0:
            answer_list.append({"model_type": key, "counts": count})

    return answer_list


def most_used_language(json_path: str) -> List[Dict[str, Any]]:
    """which language is used the most"""
    data = load_json(json_path)
    data = update_data(data)

    chinese_counts, else_counts = language_dominant_count(data)

    answer_list = []

    for key, count in chinese_counts.items():
        if count > 0:
            answer_list.append({"model_type": key, "counts": count,\
                "type": "natural", "language": "chinese"})
    for key, count in else_counts.items():
        if count > 0:
            answer_list.append({"model_type": key, "counts": count, \
                "type": "natural", "language": "else"})

    code_counts = code_language_count(data)
    for key, count in code_counts.items():
        answer_list.append({"model_type": "all", "counts": count, \
            "type": "code", "language": key})

    return answer_list

def refuse_counts(json_path: str) -> int:
    """how many refuse responses are there"""
    data = load_json(json_path)
    data = update_data(data)

    return ai_refuse_count(data)

def main():
    """base api testing"""
    data_path = "data/conversations.json"
    print(session_count(data_path))
    print(most_used_models(data_path))
    print(total_characters(data_path))
    print(most_used_language(data_path))
    print(refuse_counts(data_path))

if __name__ == "__main__":
    main()
