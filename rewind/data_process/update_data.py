"""update raw chat data"""
import datetime
from typing import Any, List, Dict
from rewind.utils.providers import ProviderType

from rewind.data_process.loading_data import load_json


def update_deepseek_data(data_list: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Loading Deepseek data"""
    new_data_list = []

    for session in data_list:
        title = session.get("title", "unknown")
        inserted_at = session.get("inserted_at", "unknown")
        updated_at = session.get("updated_at", "unknown")
        longest_interaction_list = []

        mapping = session.get("mapping", {})
        numeric_keys = [k for k in mapping.keys() if k.isdigit()]
        max_key = max(numeric_keys, key=int)

        while True:
            record = mapping.get(str(max_key), {})
            if not record:
                break
            longest_interaction_list.append(record)

            parent = record.get("parent", -1)
            if parent.isdigit():
                max_key = parent
            else:
                break
        longest_interaction_list.reverse()


        new_session = {
            "title": title,
            "inserted_at": inserted_at,
            "updated_at": updated_at,
            "longest_interaction_list": longest_interaction_list
        }
        new_data_list.append(new_session)
    return new_data_list

def _format_timestamp(timestamp: int) -> str:
    """Format timestamp to ISO string with timezone +8"""
    tz_plus_8 = datetime.timezone(datetime.timedelta(hours=8))
    date_time = datetime.datetime.fromtimestamp(timestamp, tz=tz_plus_8)
    return date_time.isoformat()


def _process_message_fragments(message: Dict[str, any]) -> tuple[List[Dict[str, any]], str]:
    """Process message fragments and return fragments list and model name"""
    fragments = []
    model = ""

    if message.get("role", "") == "assistant":
        content_list = message.get("content_list", [])
        if not content_list:
            return [], ""

        for item in content_list:
            phase = item.get("phase", "")
            meg_type = "THINK" if phase == "think" else "RESPONSE" if phase == "answer" else ""
            content = item.get("content", "")
            if meg_type:
                fragments.append({
                    "type": meg_type,
                    "content": content
                })
        model = message.get("model", "unknown")
    else:
        fragments.append({
            "type": "REQUEST",
            "content": message.get("content", "")
        })
        models = message.get("models", [])
        model = models[0] if models else "unknown"

    return fragments, model


def _find_parent_message(messages: List[Dict[str, any]], parent_id: str) -> Dict[str, any]:
    """Find parent message by ID in messages list"""
    for msg in messages:
        if msg.get("id", "") == parent_id:
            return msg
    return None


def _build_interaction_chain(messages: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Build the longest interaction chain from messages"""
    if not messages:
        return []

    interaction_chain = []
    current_msg = messages[-1]

    while current_msg:
        fragments, model = _process_message_fragments(current_msg)
        if not fragments and current_msg.get("role", "") == "assistant":
            break

        interaction_chain.append({
            'id': current_msg.get("id", ""),
            'message': {
                "model": model,
                "fragments": fragments
            }
        })

        parent_id = current_msg.get("parentId", "-1")
        if not parent_id or parent_id == "-1":
            break

        current_msg = _find_parent_message(messages, parent_id)
        if not current_msg:
            break

    interaction_chain.reverse()
    return interaction_chain


def _process_session(session: Dict[str, any]) -> Dict[str, any]:
    """Process a single session and return formatted data"""
    title = session.get("title", "unknown")
    created_at = session.get("created_at", 0)
    updated_at = session.get("updated_at", 0)

    messages = session.get("chat", {}).get("messages", [])
    interaction_chain = _build_interaction_chain(messages)

    return {
        "title": title,
        "inserted_at": _format_timestamp(created_at),
        "updated_at": _format_timestamp(updated_at),
        "longest_interaction_list": interaction_chain
    }


def update_qwen_data(raw_data_dict: Dict[str, List[Dict[str, any]]]) -> List[Dict[str, any]]:
    """Loading qwen data"""
    data_list = raw_data_dict.get("data", [])
    return [_process_session(session) for session in data_list]

def update_data(data_list: Any, provider_type: ProviderType = ProviderType.DEEPSEEK) \
    -> List[Dict[str, any]]:
    """
    Update the data list by loading only the necessary fields and clean existing data.
    """
    if provider_type == ProviderType.DEEPSEEK:
        new_data_list = update_deepseek_data(data_list)
    elif provider_type == ProviderType.QWEN:
        new_data_list = update_qwen_data(data_list)
    else:
        raise NotImplementedError(f"Provider type {provider_type} not supported yet.")

    return new_data_list


if __name__ == "__main__":
    DEEPSEEK_RAW_PATH = "data/example_deepseek.json"
    QWEN_RAW_PATH = "data/example_qwen.json"

    deepseek_data = load_json(DEEPSEEK_RAW_PATH)
    qwen_data = load_json(QWEN_RAW_PATH)

    print(update_data(deepseek_data, ProviderType.DEEPSEEK))

    print(update_data(qwen_data, ProviderType.QWEN))
