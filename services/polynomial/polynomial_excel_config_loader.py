"""Load polynomial excel config JSON and provide accessors"""
import json
import os

CONFIG_PATH = os.path.join("config", "polynomial", "polynomial_excel_config.json")

_cached = None

def load_config():
    global _cached
    if _cached is None:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _cached = json.load(f)
    return _cached

def get_required_columns_for_degree(degree: int):
    cfg = load_config()["polynomial_excel"]["required_columns"]
    return cfg.get(str(degree), [])

def get_optional_columns():
    return load_config()["polynomial_excel"].get("optional_columns", [])
