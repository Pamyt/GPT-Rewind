"""DeepSeek data processor"""
from typing import List, Dict


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
