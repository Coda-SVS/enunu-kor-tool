import os
import json
import yaml
from typing import Any


def save_json(path: str, obj: Any, indent: int = 2):
    if not path.endswith(".json"):
        path = os.path.splitext(path)[0] + ".json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent)


def load_json(path: str) -> Any:
    if not path.endswith(".json"):
        path = os.path.splitext(path)[0] + ".json"
    obj = None

    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    return obj


def save_yaml(path: str, obj: Any, indent: int = 4):
    if not path.endswith(".yaml"):
        path = os.path.splitext(path)[0] + ".yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(obj, f, indent=indent, sort_keys=False, Loader=yaml.FullLoader)


def load_yaml(path: str) -> Any:
    if not path.endswith(".yaml"):
        path = os.path.splitext(path)[0] + ".yaml"
    obj = None

    with open(path, "r", encoding="utf-8") as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj
