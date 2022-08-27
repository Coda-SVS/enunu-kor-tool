base_module_name = "enunu_kor_tool.analysis4vb.functions"


def join_module_name(func_name: str):
    if func_name.startswith("."):
        return base_module_name + func_name
    else:
        return base_module_name + "." + func_name


FUNC_LIST = {
    "lab_error_check": {"module": join_module_name("lab"), "func": "lab_error_check"},
    "phoneme_count": {"module": join_module_name("lab"), "func": "phoneme_count"},
    "phoneme_length": {"module": join_module_name("lab"), "func": "phoneme_length"},
}
