"""update raw chat data"""
from typing import Any, List, Dict
from rewind.utils.providers import ProviderType
from rewind.data_process.loading_data import load_json

# Import specific processors
from rewind.data_process.different_providers import (update_deepseek_data,
                                                     update_qwen_data,
                                                     update_claude_data)


def update_data(data_list: Any, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> List[Dict[str, any]]:
    """
    Update the data list by loading only the necessary fields and clean existing data.
    """
    if provider_type == ProviderType.DEEPSEEK:
        new_data_list = update_deepseek_data(data_list)
    elif provider_type == ProviderType.QWEN:
        new_data_list = update_qwen_data(data_list)
    elif provider_type == ProviderType.CLAUDE:
        new_data_list = update_claude_data(data_list)
    else:
        raise NotImplementedError(f"Provider type {provider_type} not supported yet.")

    return new_data_list


if __name__ == "__main__":
    DEEPSEEK_RAW_PATH = "data/example_deepseek.json"
    QWEN_RAW_PATH = "data/example_qwen.json"
    CLAUDE_RAW_PATH = "data/example_claude.json"

    deepseek_data = load_json(DEEPSEEK_RAW_PATH)
    qwen_data = load_json(QWEN_RAW_PATH)
    claude_data = load_json(CLAUDE_RAW_PATH)

    print(update_data(deepseek_data, ProviderType.DEEPSEEK))
    print(update_data(qwen_data, ProviderType.QWEN))
    print(update_data(claude_data, ProviderType.CLAUDE))
