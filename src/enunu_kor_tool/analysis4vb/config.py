import yaml

from enunu_kor_tool.analysis4vb.functions import FUNC_LIST

DEFAULT_CONFIG = {
    "output": {
        "stats": "%(db_path)s/stats",
        "graph": "%(db_path)s/stats/graph",
        "temp": "%(db_path)s/temp",
    },
    "options": {
        "log_level": "info",
        "encoding": "utf-8",
        "graph_output": True,
    },
    "funcs": list(FUNC_LIST.keys()),
    "phonemes": {
        "silence": ["pau", "sil", "br"],
        "consonant": ["g", "n", "d", "r", "l", "m", "b", "s", "j", "ch", "k", "t", "p", "h", "kk", "tt", "pp", "ss", "jj", "K", "T", "P", "N", "RR", "L", "M", "NG"],
        "vowel": ["a", "eo", "o", "u", "eu", "i", "e", "y", "w"],
        "other": ["exh", "vf", "trash"],
    },
}


def __config2yaml(config):
    config_yaml = str(yaml.dump(config, indent=2, sort_keys=False, allow_unicode=True)).split("\n")

    result = []
    count = 0
    is_funcs = False
    for line in config_yaml:
        if is_funcs:
            count += 1
            if count > 1:
                if line.strip().startswith("-"):
                    line = "# " + line
                else:
                    is_funcs = False
                    count -= 1
        elif line == "funcs:":
            is_funcs = True

        result.append(line)

    return "\n".join(result)


DEFAULT_YAML_CONFIG = __config2yaml(DEFAULT_CONFIG)
