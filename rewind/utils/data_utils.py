"""Common utility functions for data processing"""
from typing import List, Dict, Generator, Tuple


def iterate_fragments(data_list: List[Dict[str, any]]) -> Generator[Tuple[str, str], None, None]:
    """
    Generator that yields (content, interaction_type) tuples for all fragments in the data.
    """
    for session in data_list:
        interaction = session.get("longest_interaction_list", [])

        for record in interaction:
            fragments = record.get("message", {}).get("fragments", [])
            for fragment in fragments:
                content = fragment.get("content", "")
                interaction_type = fragment.get("type", "")
                yield content, interaction_type


def iterate_fragments_with_model(data_list: List[Dict[str, any]]) ->\
    Generator[Tuple[str, str, str], None, None]:
    """
    Generator that yields (content, interaction_type, model_type) tuples
    """
    for session in data_list:
        interaction = session.get("longest_interaction_list", [])

        for record in interaction:
            fragments = record.get("message", {}).get("fragments", [])
            model_type = record.get("message", {}).get("model", "unknown")
            for fragment in fragments:
                content = fragment.get("content", "")
                interaction_type = fragment.get("type", "")
                yield content, interaction_type, model_type
