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

TEMP_PATH = ""


class DataFile:
    def __init__(self) -> None:
        self._name = ""
        self._ust_path = ""
        self._lab_path = ""
        self._wav_path = ""

    def is_available(self):
        return len(self._name) != 0 and len(self._ust_path) != 0 and len(self._lab_path) != 0 and len(self._wav_path) != 0

    def set_path(self, filepath: str):
        filepath = os.path.realpath(filepath)

        if not os.path.exists(filepath):
            return False

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

    def release(self, output_path: str):
        shutil.copy2(self.ust_path, os.path.join(output_path, os.path.basename(self.ust_path)))
        shutil.copy2(self.lab_path, os.path.join(output_path, os.path.basename(self.lab_path)))
        shutil.copy2(self.wav_path, os.path.join(output_path, os.path.basename(self.wav_path)))


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
    global TEMP_PATH

    cut2sil_temppath = os.path.join(TEMP_PATH, "cut2sil")
    lab2ust_fixer_temppath = os.path.join(TEMP_PATH, "lab2ust_fixer")
    norm4wav_temppath = os.path.join(TEMP_PATH, "norm4wav")

    os.makedirs(cut2sil_temppath, exist_ok=True)
    os.makedirs(lab2ust_fixer_temppath, exist_ok=True)
    os.makedirs(norm4wav_temppath, exist_ok=True)

    for datafile in tqdm(db_files, desc="Processing...", leave=False):
        tqdm.write(f"File Name: {datafile.name}")

        # * 무음부 컷팅
        tqdm.write(f"[cut2sil] Processing...")
        output_wav_filepath, output_lab_filepath = cut2sil(datafile.wav_path, datafile.lab_path, cut2sil_temppath, "sil")
        datafile.set_path(output_wav_filepath)
        datafile.set_path(output_lab_filepath)

        # * lab 기반 ust 보정
        # TODO: ust 양자화 로직 작성
        tqdm.write(f"[lab2ust_fixer] Processing...")
        output_filepath = lab2ust_fixer(TABLE_PATH, datafile.ust_path, datafile.lab_path, lab2ust_fixer_temppath, VOWEL_LIST, USE_G2PK4UTAU)
        datafile.set_path(output_filepath)

        # * wav 노멀라이징
        tqdm.write(f"[norm4wav] Processing...")
        output_filepath = os.path.join(norm4wav_temppath, os.path.basename(datafile.wav_path))
        audio_norm(datafile.wav_path, output_filepath)
        datafile.set_path(output_filepath)

        tqdm.write(f"Release...")
        datafile.release(output_path)


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

    global TEMP_PATH

    TEMP_PATH = os.path.join(output_path, "__temp")

    os.makedirs(output_path, exist_ok=True)
    os.makedirs(TEMP_PATH, exist_ok=True)

    # ustx -> ust
    ustx2ust(input_path, os.path.join(TEMP_PATH, "ustx2ust"))

    ust_files.extend(glob(os.path.join(TEMP_PATH, "*.ust"), recursive=True))
    ust_files.extend(glob(os.path.join(TEMP_PATH, "**", "*.ust"), recursive=True))
    ust_files = list(set(ust_files))
    ust_files.sort()

    db_files: List[DataFile] = []

    def add_db(filepath: str):
        is_added = False

        for datafile in db_files:
            if datafile.is_available():
                continue
            elif datafile.set_path(filepath):
                is_added = True
                break

        if not is_added:
            datafile = DataFile()
            datafile.set_path(filepath)
            db_files.append(datafile)

    for ust_file in ust_files:
        add_db(ust_file)

    for lab_file in lab_files:
        add_db(lab_file)

    for wav_file in wav_files:
        add_db(wav_file)

    old_db_files = db_files
    db_files = []

    for db_file in old_db_files:
        if db_file.is_available():
            db_files.append(db_file)
        else:
            print(f"삭제됨: {db_file}")

    print(f"Info: 데이터 파일 개수: [{len(db_files)}]")

    preprocess(db_files, output_path)

    shutil.rmtree(TEMP_PATH, ignore_errors=True)

    print("done.")


if __name__ == "__main__":
    main()
