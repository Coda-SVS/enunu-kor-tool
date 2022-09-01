import os
from typing import Any, Dict
import yaml

from enunu_kor_tool.analysis4vb.functions import FUNC_LIST

DEFAULT_CONFIG = {
    "output": {
        "stats": "%(db_path)s/analysis/stats",
        "graph": "%(db_path)s/analysis/stats/graph",
        "temp": "%(db_path)s/analysis/temp",
    },
    "options": {
        "log_level": "info",
        "encoding": "utf-8",
        "graph_save": True,
        "graph_show": False,
        "graph_darkmode": True,
        "graph_show_dpi": 100,
    },
    "funcs": list(FUNC_LIST.keys()),
    "group": {
        "silence": ["R", "pau", "sil", "br"],
        "consonant": ["g", "n", "d", "r", "l", "m", "b", "s", "j", "ch", "k", "t", "p", "h", "kk", "tt", "pp", "ss", "jj", "K", "T", "P", "N", "RR", "L", "M", "NG"],
        "vowel": ["a", "eo", "o", "u", "eu", "i", "e", "y", "w"],
        "other": ["exh", "vf", "trash"],
    },
}


def config2yaml(config: Dict[str, Any]):
    default_options = {
        "indent": 2,
        "sort_keys": False,
        "allow_unicode": True,
    }
    result = []

    for key in config.keys():
        if key == "group":
            result.append(yaml.dump({key: config[key]}, default_flow_style=None, **default_options))
        else:
            result.append(yaml.dump({key: config[key]}, **default_options))

    return "".join(result)


def save_config2yaml(path: str, config: Dict[str, Any]):
    if not path.endswith(".yaml"):
        path = os.path.splitext(path)[0] + ".yaml"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(config2yaml(config))


def save_default_config2yaml(path: str):
    if not path.endswith(".yaml"):
        path = os.path.splitext(path)[0] + ".yaml"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(DEFAULT_YAML_CONFIG)


DEFAULT_YAML_CONFIG = config2yaml(DEFAULT_CONFIG)
