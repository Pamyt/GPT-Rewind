"""analyze time data"""
from typing import List, Dict, Any
from rewind.utils.time_utils import extract_time, delta_to_dhms

def chat_frequency_distribution(data_list: List[Dict[str, Any]]) -> Dict[Any, Any]:
    """analyze chat frequency distribution"""
    month_frequency_distribution = {}
    day_frequency_distribution = {}
    for session in data_list:
        create_time = session.get("inserted_at", "")
        if create_time:
            create_time_ym = create_time[:7]  # Extract "YYYY-MM"
            if create_time_ym not in month_frequency_distribution:
                month_frequency_distribution[create_time_ym] = 0
            month_frequency_distribution[create_time_ym] += 1
            create_time_ymd = create_time[:10]  # Extract "YYYY-MM-DD"
            if create_time_ymd not in day_frequency_distribution:
                day_frequency_distribution[create_time_ymd] = 0
            day_frequency_distribution[create_time_ymd] += 1

    return {"month_distribution": month_frequency_distribution,
            "day_distribution": day_frequency_distribution}


def _find_most_active_session(data_list: List[Dict[str, Any]]) -> tuple:
    """find the session with the most interactions"""
    max_interaction_count = 0
    max_interaction_session = None

    for session in data_list:
        interactions = session.get("longest_interaction_list", [])
        interaction_count = len(interactions)
        if interaction_count > max_interaction_count:
            max_interaction_count = interaction_count
            max_interaction_session = session

    return max_interaction_session, max_interaction_count


def _find_most_response_session(data_list: List[Dict[str, Any]]) -> tuple:
    """find the session with the most response characters"""
    max_response_char_count = 0
    max_response_session = None

    for session in data_list:
        interactions = session.get("longest_interaction_list", [])
        response_char_count = 0
        for record in interactions:
            fragments = record.get("message", {}).get("fragments", [])
            for fragment in fragments:
                if fragment.get("type", "") in ("RESPONSE", "THINK"):
                    content = fragment.get("content", "")
                    response_char_count += len(content)
        if response_char_count > max_response_char_count:
            max_response_char_count = response_char_count
            max_response_session = session

    return max_response_session, max_response_char_count


def _find_longest_duration_session(data_list: List[Dict[str, Any]]) -> tuple:
    """find the session with the longest duration"""
    max_total_seconds = 0
    max_last_time_session = None
    days, hours, minutes, seconds = 0, 0, 0, 0

    for session in data_list:
        inserted_at = session.get("inserted_at", "")
        updated_at = session.get("updated_at", "")
        if inserted_at and updated_at:
            current_days, current_hours, current_minutes,\
                current_seconds, total_seconds =\
                delta_to_dhms(inserted_at, updated_at)
            if total_seconds > max_total_seconds:
                max_total_seconds = total_seconds
                max_last_time_session = session
                days, hours, minutes, seconds =\
                    current_days, current_hours, current_minutes, current_seconds

    return max_last_time_session, max_total_seconds, days, hours, minutes, seconds


def _find_earliest_latest_sessions(data_list: List[Dict[str, Any]]) -> tuple:
    """find the earliest and latest sessions"""
    earliest_time = None
    earliest_session = None
    latest_time = None
    latest_session = None

    for session in data_list:
        inserted_at = session.get("inserted_at", "")
        if inserted_at:
            chat_start_time = extract_time(inserted_at)
            if earliest_time is None or chat_start_time < earliest_time:
                earliest_time = chat_start_time
                earliest_session = session
            if latest_time is None or chat_start_time > latest_time:
                latest_time = chat_start_time
                latest_session = session

    return earliest_session, earliest_time, latest_session, latest_time


def chat_themost(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """find the session with the most interactions"""
    most_active_session, max_interaction_count = _find_most_active_session(data_list)
    most_response_session, max_response_char_count = _find_most_response_session(data_list)
    longest_duration_session, longest_duration_seconds, days, hours, minutes, seconds =\
        _find_longest_duration_session(data_list)
    earliest_session, earliest_time, latest_session, latest_time =\
        _find_earliest_latest_sessions(data_list)

    return {
        "most_active_session": most_active_session,
        "max_interaction_count": max_interaction_count,
        "most_response_session": most_response_session,
        "max_response_char_count": max_response_char_count,
        "longest_duration_session": longest_duration_session,
        "longest_duration_seconds": longest_duration_seconds,
        "longest_duration_dhms": f"{days}d {hours}h {minutes}m {seconds}s",
        "earliest_session": earliest_session,
        "earliest_time": earliest_time,
        "latest_session": latest_session,
        "latest_time": latest_time
    }
