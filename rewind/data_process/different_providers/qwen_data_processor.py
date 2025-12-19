"""Qwen data processor"""
from typing import List, Dict
from rewind.utils.common_utils import process_session


def update_qwen_data(raw_data_dict: Dict[str, List[Dict[str, any]]]) -> List[Dict[str, any]]:
    """Loading qwen data"""
    data_list = raw_data_dict.get("data", [])
    return [process_session(session) for session in data_list]
