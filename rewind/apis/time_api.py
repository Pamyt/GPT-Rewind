"""time related api for data overview"""
from typing import Dict, List, Any

from rewind.data_process import (
    load_json,
    update_data,
    chat_frequency_distribution,
    chat_themost,
    count_per_hour_distribution,
)
from rewind.utils.providers import ProviderType

def chat_days(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> List[Dict[str, Any]]:
    """each day chat frequency"""

    data = load_json(json_path)
    data = update_data(data, provider_type=provider_type)

    full_distribution = chat_frequency_distribution(data)
    day_distribution = full_distribution["day_distribution"]

    answer_list = []
    for time, count in day_distribution.items():
        answer_list.append({"date": time, "counts": count})

    return answer_list

def time_limit(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> List[Dict[str, Any]]:
    """time limit for earliest and latest"""

    data = load_json(json_path)
    data = update_data(data, provider_type=provider_type)

    full_distribution = chat_themost(data)
    earliest_time = full_distribution["earliest_time"]
    latest_time = full_distribution["latest_time"]
    earliest_session = full_distribution["earliest_session"]
    latest_session = full_distribution["latest_session"]

    return [{"earliest_time": earliest_time}, {"latest_time": latest_time},
            {"earliest_session": earliest_session}, {"latest_session": latest_session}]

def per_hour_distribution(json_path: str, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> Dict[Any, Any]:
    """distribution of sessions across 24 hours of the day"""

    data = load_json(json_path)
    data = update_data(data, provider_type=provider_type)

    hour_distribution = count_per_hour_distribution(data)

    return hour_distribution

def main():
    """main function"""
    data_path = "data/qwen_conversations.json"
    print(chat_days(data_path, provider_type= ProviderType.QWEN))
    print(time_limit(data_path, provider_type= ProviderType.QWEN))
    print(per_hour_distribution(data_path, provider_type= ProviderType.QWEN))


if __name__ == "__main__":
    main()
