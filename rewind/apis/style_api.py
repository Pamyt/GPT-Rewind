"""style api for data overview"""

from typing import List, Dict, Any
from rewind.data_process import (
    emoji_count as _emoji_count,
    polite_count,
    load_json,
    update_data,
)

def emoji_counts(json_path: str) -> List[Dict[str, Any]]:
    """counting each emoji times"""

    data = load_json(json_path)
    data = update_data(data)

    return _emoji_count(data)




def polite_extent(json_path: str) -> List[Dict[str, Any]]:
    """counting polite and impolite words, returns list of dicts"""

    data = load_json(json_path)
    data = update_data(data)

    return polite_count(data)


def main():
    """main function"""

    data_path = "data/conversations.json"
    print(emoji_counts(data_path))
    print(polite_extent(data_path))




if __name__ == "__main__":
    main()
