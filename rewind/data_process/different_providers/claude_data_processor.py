"""Claude data processor"""
from typing import List, Dict
from rewind.utils.common_utils import utc_to_iso_plus8


def update_claude_data(data_list: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Loading Claude data"""
    new_data_list = []

    for session in data_list:
        title = session.get("name", "unknown")
        created_at = utc_to_iso_plus8(session.get("created_at", "unknown"))
        updated_at = utc_to_iso_plus8(session.get("updated_at", "unknown"))
        chat_messages = session.get("chat_messages", [])
        longest_interaction_list = []

        for message in chat_messages:
            fragments = []
            if message.get("sender", "") == "assistant":
                content_list = message.get("content", [])
                for item in content_list:
                    content = item.get("text", "")
                    fragments.append({
                        "type": "RESPONSE",
                        "content": content
                    })
            else:
                fragments.append({
                    "type": "REQUEST",
                    "content": message.get("text", "")
                })

            longest_interaction_list.append({
                'id': message.get("uuid", ""),
                'message': {
                    "model": "claude",  # Claude does not provide model per message
                    "fragments": fragments
                }
            })

        new_session = {
            "title": title,
            "inserted_at": created_at,
            "updated_at": updated_at,
            "longest_interaction_list": longest_interaction_list
        }
        new_data_list.append(new_session)
    return new_data_list
