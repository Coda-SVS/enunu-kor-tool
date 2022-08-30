import cli_ui

BASE_MODULE_NAME = "enunu_kor_tool.analysis4vb.functions"


def join_module_name(func_name: str):
    if func_name.startswith("."):
        return BASE_MODULE_NAME + func_name
    else:
        return BASE_MODULE_NAME + "." + func_name


MODULE_DICT = {
    # "g2pk4utau": {"module": "enunu_kor_tool.g2pk4utau.g2pk4utau", "func": "cli_ui_main"},
    # "ustx2lab": {"module": "enunu_kor_tool.entry.ustx2lab", "func": "cli_ui_main"},
    # "lab2ntlab": {"module": "enunu_kor_tool.entry.lab2ntlab", "func": "cli_ui_main"},
    "analysis4vb": {"module": "enunu_kor_tool.analysis4vb.analysis", "func": "cli_ui_main"},
}


MODULE_LIST = [
    # "g2pk4utau",
    # "ustx2lab",
    # "lab2ntlab",
    "analysis4vb",
]


MODULE_DESC_LIST = {
    # "g2pk4utau",
    # "ustx2lab",
    # "lab2ntlab",
    "analysis4vb": "analysis4vb (ENUNU 통계 모듈)",
}


def main():
    global MODULE_LIST

    selected_module = cli_ui.ask_choice("사용할 모듈을 선택하세요.", choices=MODULE_LIST, func_desc=lambda m: MODULE_DESC_LIST[m])

    module_info = MODULE_DICT[selected_module]
    module = __import__(module_info["module"], fromlist=[module_info["module"]])
    func = getattr(module, module_info["func"])

    func()


if __name__ == "__main__":
    main()
