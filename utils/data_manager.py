import json
from datetime import datetime

class DataManager:
    def __init__(self, filename='simulation_data.json'):
        self.filename = filename

    def save_data(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_simulation_result(self, result):
        data = self.load_data()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['last_simulation'] = {
            'result': result,
            'timestamp': timestamp
        }
        self.save_data(data)

    def load_last_simulation_result(self):
        data = self.load_data()
        if not data:
            print("No data found or empty file.")
            return None
        return data.get('last_simulation')