import json
import os

BASE_PATH = os.path.join(os.path.dirname(__file__), "base_embrapa.json")

def carregar_base_embrapa():
    with open(BASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)