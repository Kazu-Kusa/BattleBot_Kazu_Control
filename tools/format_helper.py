import json


def format_json_file(file_path):
    with open(file_path) as file:
        try:
            json_data = json.load(file)
            formatted_json = json.dumps(json_data, indent=4, ensure_ascii=False)
            return formatted_json
        except json.JSONDecodeError as e:
            return f"Failed to parse JSON: {e}"
