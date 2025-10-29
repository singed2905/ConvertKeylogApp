import json

class FileUtils:
    @staticmethod
    def load_modes_from_json(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('modes', [])
