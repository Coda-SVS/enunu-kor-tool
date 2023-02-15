import os
import shutil
from glob import glob
from typing import List

from tqdm import tqdm

from enunu_kor_tool.utaupyk._ustx2ust import ustx2ust
from enunu_kor_tool.entry.cut2sil import cut2sil
from enunu_kor_tool.entry.lab2ust_fixer import lab2ust_fixer
from enunu_kor_tool.entry.norm4wav import audio_norm

TABLE_PATH = ""
VOWEL_LIST = []
USE_G2PK4UTAU = True

UST_TEMP_PATH = ""
LAB_TEMP_PATH = ""
WAV_TEMP_PATH = ""


class DataFile:
    def __init__(self) -> None:
        self._name = ""
        self._ust_path = ""
        self._lab_path = ""
        self._wav_path = ""

    def is_available(self):
        return len(self._name) != 0 and len(self._ust_path) != 0 and len(self._lab_path) != 0 and len(self._wav_path) != 0

    def add_path(self, filepath: str):
        name, ext = os.path.splitext(os.path.basename(filepath))

        if len(self._name) == 0:
            self._name = name

        if self._name == name:
            if ext == ".ust":
                self._ust_path = filepath
            elif ext == ".lab":
                self._lab_path = filepath
            elif ext == ".wav":
                self._wav_path = filepath

            return True
        return False

    @property
    def name(self):
        return self._name

    @property
    def ust_path(self):
        return self._ust_path

    @ust_path.setter
    def ust_path(self, value):
        name, ext = os.path.splitext(os.path.basename(value))

        if len(self._name) == 0:
            self._name = name

        self._ust_path = value

    @property
    def lab_path(self):
        return self._lab_path

    @property
    def wav_path(self):
        return self._wav_path

    def __repr__(self) -> str:
        result = f"[{self._name}]"
        if len(self._ust_path) > 0:
            result += f"\n    ust_path: {self._ust_path}"
        if len(self._lab_path) > 0:
            result += f"\n    lab_path: {self._lab_path}"
        if len(self._wav_path) > 0:
            result += f"\n    wav_path: {self._wav_path}"
        return result

    def __str__(self) -> str:
        return self.__repr__()


def cli_ui_main():
    import cli_ui

    print("> 설명: 해당 모듈은 DB에 대한 전체적인 전처리를 모두 수행합니다.")
    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["table"] = cli_ui.ask_string("table 파일 경로를 입력하세요.")
    args["vowel_list"] = cli_ui.ask_string("모음 리스트를 입력하세요. (,로 구분)")
    args["input"] = cli_ui.ask_string("DB 폴더 경로를 입력하세요.")
    args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력하세요.")
    args["notuse_g2pk4utau"] = cli_ui.ask_yes_no("g2pk4utau 미사용", default=False)

    main(args)


# def copy_dir(source_dir: str, dist_dir: str):
#     assert os.path.exists(source_dir), "소스 디렉터리를 찾을 수 없습니다."
#     assert not os.path.exists(dist_dir), "목적 경로가 비어있지 않습니다."
#     shutil.copytree(source_dir, dist_dir)


def get_db_files(input_path: str):
    ust_files = glob(os.path.join(input_path, "*.ust"), recursive=True)
    ust_files.extend(glob(os.path.join(input_path, "**", "*.ust"), recursive=True))
    ust_files = list(set(ust_files))
    ust_files.sort()

    lab_files = glob(os.path.join(input_path, "*.lab"), recursive=True)
    lab_files.extend(glob(os.path.join(input_path, "**", "*.lab"), recursive=True))
    lab_files = list(set(lab_files))
    lab_files.sort()

    wav_files = glob(os.path.join(input_path, "*.wav"), recursive=True)
    wav_files.extend(glob(os.path.join(input_path, "**", "*.wav"), recursive=True))
    wav_files = list(set(wav_files))
    wav_files.sort()

    return ust_files, lab_files, wav_files


def preprocess(db_files: List[DataFile], output_path: str):  # 전처리
    global TABLE_PATH, VOWEL_LIST, USE_G2PK4UTAU
    global UST_TEMP_PATH, LAB_TEMP_PATH, WAV_TEMP_PATH

    for datafile in tqdm(db_files, desc="Processing..."):
        lab2ust_fixer(TABLE_PATH, datafile.ust_path, datafile.lab_path, , VOWEL_LIST, USE_G2PK4UTAU)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="DB에 대한 전체적인 전처리를 모두 수행합니다.")

        parser.add_argument("-d", dest="table", required=True, help="table 파일 경로")
        parser.add_argument("-p", dest="vowel_list", required=True, help="모음 리스트 (,로 구분)")  # kor: a,eo,o,u,i,eu,e,y,w
        parser.add_argument("-i", dest="input", required=True, help="DB 폴더 경로")
        parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")
        parser.add_argument("--no-g2p", dest="notuse_g2pk4utau", action="store_false", help="g2pk4utau를 사용하지 않습니다.")

        args = vars(parser.parse_args())

    global TABLE_PATH, VOWEL_LIST, USE_G2PK4UTAU

    TABLE_PATH = args["table"]
    _vowel_list: str = args["vowel_list"]
    VOWEL_LIST = [v.strip() for v in _vowel_list.split(",")]

    input_path = args["input"]
    output_path = args["output"]

    USE_G2PK4UTAU = args["notuse_g2pk4utau"]

    ust_files, lab_files, wav_files = get_db_files(input_path=input_path)

    if 0 == len(ust_files) == len(lab_files) == len(wav_files):
        print("Error !: 데이터 파일을 찾을 수 없습니다.")
        return

    if len(ust_files) != len(lab_files) != len(wav_files):
        print("Error !: 각 분류별 데이터 파일의 수가 일치하지 않습니다")
        return

    # main logic

    temp_path = os.path.join(output_path, "__temp")

    os.makedirs(output_path, exist_ok=True)
    os.makedirs(temp_path, exist_ok=True)

    global UST_TEMP_PATH, LAB_TEMP_PATH, WAV_TEMP_PATH

    UST_TEMP_PATH = os.path.join(temp_path, "ust")
    LAB_TEMP_PATH = os.path.join(temp_path, "lab")
    WAV_TEMP_PATH = os.path.join(temp_path, "wav")
    os.makedirs(UST_TEMP_PATH, exist_ok=True)
    os.makedirs(LAB_TEMP_PATH, exist_ok=True)
    os.makedirs(WAV_TEMP_PATH, exist_ok=True)

    # ustx -> ust
    ustx2ust(input_path, os.path.join(UST_TEMP_PATH, "ustx2ust"))

    ust_files.extend(glob(os.path.join(UST_TEMP_PATH, "*.ust"), recursive=True))
    ust_files.extend(glob(os.path.join(UST_TEMP_PATH, "**", "*.ust"), recursive=True))
    ust_files = list(set(ust_files))
    ust_files.sort()

    db_files: List[DataFile] = []

    def add_db(filepath: str):
        is_added = False

        for datafile in db_files:
            if datafile.is_available():
                continue
            elif datafile.add_path(filepath):
                is_added = True
                break

        if not is_added:
            datafile = DataFile()
            datafile.add_path(filepath)
            db_files.append(datafile)

    for ust_file in ust_files:
        add_db(ust_file)

    for lab_file in lab_files:
        add_db(lab_file)

    for wav_file in wav_files:
        add_db(wav_file)

    for idx in range(len(db_files) - 1, 0, -1):
        if db_files[idx].is_available():
            continue
        else:
            print(f"삭제됨: {db_files[idx]}")
            del db_files[idx]

    print(f"Info: 데이터 파일 개수: [{len(db_files)}]")

    preprocess(db_files, output_path)

    print("done.")


if __name__ == "__main__":
    main()
