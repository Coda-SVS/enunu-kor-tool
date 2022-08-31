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


def save_yaml(path: str, obj: Any, indent: int = 2):
    if not path.endswith(".yaml"):
        path = os.path.splitext(path)[0] + ".yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(obj, f, indent=indent, sort_keys=False, allow_unicode=True)


def load_yaml(path: str) -> Any:
    if not path.endswith(".yaml"):
        path = os.path.splitext(path)[0] + ".yaml"
    obj = None

    with open(path, "r", encoding="utf-8") as f:
        obj = yaml.load(f, Loader=yaml.FullLoader)

    return obj


IS_MATPLOTLIB_INIT = False
PLOT_COUNT_DICT = {}


def matplotlib_init(useDarkMode: bool = True):
    global IS_MATPLOTLIB_INIT

    if not IS_MATPLOTLIB_INIT:
        import matplotlib
        from matplotlib import pyplot

        matplotlib.rcParams["font.family"] = "Malgun Gothic"
        matplotlib.rcParams["axes.unicode_minus"] = False
        IS_MATPLOTLIB_INIT = True

        if useDarkMode:
            pyplot.style.use(["dark_background"])


def get_plot_num(plot_name: str) -> int:
    global PLOT_COUNT_DICT

    if plot_name in PLOT_COUNT_DICT:
        return PLOT_COUNT_DICT[plot_name]
    else:
        count = PLOT_COUNT_DICT[plot_name] = len(PLOT_COUNT_DICT)
        return count
