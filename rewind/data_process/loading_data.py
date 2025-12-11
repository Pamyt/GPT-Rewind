"""Loading json data"""
import json


def load_json(file_path: str):
    """loading json"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data



if __name__ == "__main__":
    # Example usage
    sample_data = load_json('data/example.json')
    print(sample_data[0].keys())
