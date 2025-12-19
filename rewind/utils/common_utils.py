"""Common utility functions for data processing"""
import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Tuple


def format_timestamp(timestamp: int) -> str:
    """Format timestamp to ISO string with timezone +8"""
    tz_plus_8 = datetime.timezone(datetime.timedelta(hours=8))
    date_time = datetime.datetime.fromtimestamp(timestamp, tz=tz_plus_8)
    return date_time.isoformat()


def utc_to_iso_plus8(iso_str: str) -> str:
    """Convert UTC ISO string to ISO string with +8 timezone"""
    if iso_str == "unknown":
        return "unknown"
    dt_utc = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    dt_plus8 = dt_utc.astimezone(ZoneInfo("Asia/Shanghai"))
    return dt_plus8.isoformat()


def process_message_fragments(message: Dict[str, any]) -> Tuple[List[Dict[str, any]], str]:
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


def find_parent_message(messages: List[Dict[str, any]], parent_id: str) -> Dict[str, any]:
    """Find parent message by ID in messages list"""
    for msg in messages:
        if msg.get("id", "") == parent_id:
            return msg
    return None


def build_interaction_chain(messages: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Build the longest interaction chain from messages"""
    if not messages:
        return []

    interaction_chain = []
    current_msg = messages[-1]

    while current_msg:
        fragments, model = process_message_fragments(current_msg)
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

        current_msg = find_parent_message(messages, parent_id)
        if not current_msg:
            break

    interaction_chain.reverse()
    return interaction_chain


def process_session(session: Dict[str, any]) -> Dict[str, any]:
    """Process a single session and return formatted data"""
    title = session.get("title", "unknown")
    created_at = session.get("created_at", 0)
    updated_at = session.get("updated_at", 0)

    messages = session.get("chat", {}).get("messages", [])
    interaction_chain = build_interaction_chain(messages)

    return {
        "title": title,
        "inserted_at": format_timestamp(created_at),
        "updated_at": format_timestamp(updated_at),
        "longest_interaction_list": interaction_chain
    }
