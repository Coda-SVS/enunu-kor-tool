from glob import glob
import os
from copy import deepcopy
from typing import Dict, List


DEFAULT_LANG = {}

KO = {
    "[{selected_lang}] 언어가 설정되었습니다.": "[{selected_lang}] 언어가 설정되었습니다.",
}


def is_not_null_str(s: str):
    return s != None and s != "" and not s.isspace()


class Lang:
    def __init__(self, lang_dict: Dict[str, str]) -> None:
        self._lang_dict = lang_dict

    def __call__(self, key: str, **kwargs) -> str:
        msg = None

        if self._lang_dict != None:
            msg = self._lang_dict.get(key)

        if not is_not_null_str(msg):
            msg = KO.get(key, "명시되어 있지 않은 메시지 입니다.")

        return msg.format(**kwargs)


def save_lang(lang_file_path: str, lang: Dict[str, str]):
    if (dirpath := os.path.dirname(lang_file_path)) != "" and not dirpath.isspace():
        os.makedirs(dirpath, exist_ok=True)

    lines = []
    for k, v in lang.items():
        lines.append("> " + k.replace("\n", "\\n"))
        if k == v:
            lines.append("= ")
        else:
            lines.append("= " + v.replace("\n", "\\n"))

    with open(lang_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def load_lang(lang_file_path: str):
    if not os.path.isfile(lang_file_path):
        return {}

    result = deepcopy(KO)

    lines: List[str] = []
    with open(lang_file_path, "r", encoding="utf-8") as f:
        lines.extend(f.readlines())

    key = ""
    for idx, line in enumerate(lines):
        if line.startswith(">"):
            key = line[1:].strip()
        elif line.startswith("="):
            val = line[1:].strip()
            if is_not_null_str(key) and is_not_null_str(val) and key in result:
                result[key] = val
                key = ""
        else:
            print(f"언어 파일 파싱 실패: line=[{str(idx).rjust(4)}], text=[{line}]")

    return result


def set_global_lang(lang_file_path: str = ""):
    global KO, DEFAULT_LANG, CURRENT_LANG

    if not is_not_null_str(lang_file_path) or not os.path.isfile(lang_file_path):
        print("언어 파일을 찾을 수 없습니다. 내장된 언어 사용됨: [ko]")
        DEFAULT_LANG = KO
    else:
        DEFAULT_LANG = load_lang(lang_file_path)

    CURRENT_LANG = Lang(DEFAULT_LANG)


AVAILABLE_LANG_DICT = {}

CURRENT_LANG = None


def get_global_lang():
    global CURRENT_LANG

    if CURRENT_LANG == None:
        set_global_lang()


def cli_ui_main():
    import cli_ui

    global CURRENT_LANG

    selected_lang = cli_ui.ask_choice("사용할 언어를 선택하세요. (Please select a language.)", choices=list(AVAILABLE_LANG_DICT.keys()))

    lang = load_lang(AVAILABLE_LANG_DICT[selected_lang])

    CURRENT_LANG = Lang(lang)

    print(CURRENT_LANG("[{selected_lang}] 언어가 설정되었습니다.", selected_lang=selected_lang))


LANG_DIR_PATH = os.environ.get("LANG_DIR_PATH")
if LANG_DIR_PATH == "" or LANG_DIR_PATH == None or LANG_DIR_PATH.isspace():
    LANG_DIR_PATH = "lang"

if not os.path.isdir(LANG_DIR_PATH) or len(os.listdir(LANG_DIR_PATH)) == 0:
    os.makedirs(LANG_DIR_PATH, exist_ok=True)

    save_lang(ko_path := os.path.join(LANG_DIR_PATH, "ko.lang"), KO)
    AVAILABLE_LANG_DICT["ko"] = ko_path
else:
    lang_files = glob(os.path.join(LANG_DIR_PATH, "*.lang"))
    for path in lang_files:
        save_lang(path, load_lang(path))  # 새로운 lang 파일로 업데이트
        AVAILABLE_LANG_DICT[os.path.splitext(os.path.basename(path))[0]] = path