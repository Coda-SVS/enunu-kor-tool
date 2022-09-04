import os
import shutil
import time
from glob import glob
from typing import List

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from enunu_kor_tool import log, utils, lang
from enunu_kor_tool.entry import ustx2lab

L = lang.get_global_lang()


class UST_LAB_FileWatcher(FileSystemEventHandler):
    def __init__(self, db_path: str, table_path: str, temp_path: str, use_g2pk4utau: bool) -> None:
        super().__init__()
        self._logger = log.get_logger("UST_LAB_FileWatcher")
        self._db_path = db_path
        self._table_path = table_path
        self._temp_path = temp_path
        self._use_g2pk4utau = use_g2pk4utau

    def temp_path_filter(self, paths: List[str]):
        return list(filter(lambda p: self._temp_path not in p, paths))

    def on_modified(self, event: FileSystemEvent):
        if self._temp_path in event.src_path:
            return

        if event.event_type == "modified":
            param_dict = {}
            filepath = event.src_path

            logger = self._logger
            logger.info(L("변경사항이 감지되었습니다. Path={path}", path=filepath))

            filename, ext = os.path.splitext(os.path.basename(filepath))
            if ext == ".ustx":
                param_dict["ust_ustx_path"] = filepath
            if ext == ".ust":
                param_dict["ust_ustx_path"] = filepath
            if ext == ".lab":
                param_dict["lab_path"] = filepath

            if "ust_ustx_path" in param_dict:
                lab_file = glob(os.path.join(self._db_path, "**", f"{filename}.lab"), recursive=True)
                lab_file += glob(os.path.join(self._db_path, f"{filename}.lab"), recursive=True)
                lab_file = self.temp_path_filter(list(set(lab_file)))
                if len(lab_file) == 0:
                    logger.warning(L("{filename}.lab 파일을 찾을 수 없습니다.", filename=filename))
                else:
                    param_dict["lab_path"] = lab_file[0]
            else:
                ustx_file = glob(os.path.join(self._db_path, "**", f"{filename}.ustx"), recursive=True)
                ustx_file += glob(os.path.join(self._db_path, f"{filename}.ustx"), recursive=True)
                ustx_file = self.temp_path_filter(list(set(ustx_file)))
                if len(ustx_file) > 0:
                    param_dict["ust_ustx_path"] = ustx_file[0]
                else:
                    ust_file = glob(os.path.join(self._db_path, "**", f"{filename}.ust"), recursive=True)
                    ust_file += glob(os.path.join(self._db_path, f"{filename}.ust"), recursive=True)
                    ust_file = self.temp_path_filter(list(set(ust_file)))
                    if len(ust_file) == 0:
                        logger.warning(L("{filename}.ustx 또는 {filename}.ust 파일을 찾을 수 없습니다.", filename=filename))
                    else:
                        param_dict["ust_ustx_path"] = lab_file[0]

            param_dict["table_path"] = self._table_path
            param_dict["temp_path"] = self._temp_path
            param_dict["use_g2pk4utau"] = self._use_g2pk4utau
            compare_ust_lab(**param_dict)


def compare_ust_lab(table_path: str, ust_ustx_path: str, lab_path: str, temp_path: str, use_g2pk4utau: bool):
    logger = log.get_logger(compare_ust_lab)

    if not utils.is_not_null_str(table_path) or not os.path.isfile(table_path):
        logger.error(L("{path}에 파일이 존재하지 않습니다.", path=table_path))
    if not utils.is_not_null_str(ust_ustx_path) or not os.path.isfile(table_path):
        logger.error(L("{path}에 파일이 존재하지 않습니다.", path=ust_ustx_path))
    if not utils.is_not_null_str(lab_path) or not os.path.isfile(table_path):
        logger.error(L("{path}에 파일이 존재하지 않습니다.", path=lab_path))
    if not utils.is_not_null_str(temp_path) or not os.path.isfile(table_path):
        logger.error(L("{path}에 폴더가 존재하지 않습니다.", path=temp_path))

    silence_phn_list = ["pau", "sil"]

    temp_ust_ustx_path = os.path.join(temp_path, os.path.basename(ust_ustx_path))
    shutil.copy(ust_ustx_path, temp_ust_ustx_path)
    ust_ustx_path = temp_ust_ustx_path

    filename = os.path.splitext(os.path.basename(ust_ustx_path))[0]
    score_lab = os.path.join(temp_path, f"{filename}.lab")
    ustx2lab.ustx2lab(table_path, ust_ustx_path, temp_path, use_g2pk4utau=use_g2pk4utau)

    align_lab_lines = None
    score_lab_lines = None

    with open(lab_path, "r", encoding="utf-8") as f:
        align_lab_lines = f.readlines()

    with open(score_lab, "r", encoding="utf-8") as f:
        score_lab_lines = f.readlines()

    null_filter = lambda t: t != ""
    align_lab_lines = list(filter(null_filter, [l.rstrip("\n") for l in align_lab_lines]))
    score_lab_lines = list(filter(null_filter, [l.rstrip("\n") for l in score_lab_lines]))

    is_error = False

    idx = 0
    try:
        score_lab_lines_len = len(score_lab_lines)
        for idx, align_line in enumerate(align_lab_lines):
            if idx >= score_lab_lines_len:
                for line in align_lab_lines[idx:]:
                    align_phn = " ".join(line.split(" ")[2:])

                    if align_phn.strip(" ") != align_phn:
                        logger.error(L("라벨 파일에 불필요한 문자가 포함된 표현이 있습니다. LineNum=[{line}]", line=idx + 1))
                        is_error = True
                    elif align_phn not in silence_phn_list:
                        logger.error(L("DB의 라벨 파일과 악보에서 생성한 라벨 파일의 길이가 다릅니다. filename=[{filename}]", filename=filename))
                        is_error = True
                        break
                break

            align_start, align_end, *align_phn = align_line.split(" ")
            score_start, score_end, *score_phn = score_lab_lines[idx].split(" ")
            align_start = int(align_start)
            align_end = int(align_end)
            align_phn = " ".join(align_phn)
            score_start = int(score_start)
            score_end = int(score_end)
            score_phn = " ".join(score_phn)

            if align_phn.strip(" ") != align_phn:
                logger.error(L("라벨 파일에 불필요한 문자가 포함된 표현이 있습니다. LineNum=[{line}]", line=idx + 1))
                is_error = True
            if align_phn != score_phn and (score_phn not in silence_phn_list and align_phn not in silence_phn_list):
                logger.error(
                    L(
                        (
                            "라벨 파일에 오류가 있습니다.\n"
                            "DB 라벨 파일: LineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]\n"
                            "UST(X)에서 생성된 라벨 파일: Start=[{score_start}], End=[{score_end}], Phoneme=[{score_phn}]"
                        ),
                        line=idx + 1,
                        align_start=align_start,
                        align_end=align_end,
                        align_phn=align_phn,
                        score_start=score_start,
                        score_end=score_end,
                        score_phn=score_phn,
                    )
                )
                is_error = True
            if align_start >= align_end:
                logger.error(
                    L(
                        "라벨 파일에 시작 시간이 종료 시간 보다 느린 음소가 있습니다.\nLineNum=[{line}], Start=[{align_start}], End=[{align_end}], Phoneme=[{align_phn}]",
                        line=idx + 1,
                        align_start=align_start,
                        align_end=align_end,
                        align_phn=align_phn,
                    )
                )
                is_error = True
    except:
        logger.error(L("라벨 파일을 점검하는 도중 파싱 오류가 발생했습니다. LineNum=[{line}]", line=idx + 1))
        is_error = True

    if not is_error:
        logger.info(L("라벨 파일에서 오류를 발견하지 못했습니다."))


def cli_ui_main():
    import cli_ui

    print(L("> 설명: 해당 모듈은 ustx, ust <-> lab 일치 여부를 검사합니다."))
    print(L("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다."))

    args = {}

    args["table"] = cli_ui.ask_string(L("table 파일 경로를 입력하세요."))
    args["input"] = cli_ui.ask_string(L("DB 폴더의 경로를 입력하세요."))
    args["use_g2pk4utau"] = cli_ui.ask_yes_no(L("g2pk4utau 사용 여부"), default=True)

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="ustx, ust <-> lab 일치 여부를 검사합니다.")

        parser.add_argument("-d", dest="table", required=True, help="table 파일 경로")
        parser.add_argument("-i", dest="input", required=True, help="데이터 셋의 경로")
        parser.add_argument("--no-g2p", dest="use_g2pk4utau", action="store_false", help="g2pk4utau 사용 안함")

        args = vars(parser.parse_args())

    db_path = args["input"].rstrip("\\")

    logger = log.get_logger(main)

    db_temp_path = os.path.join(args["input"], "temp")

    if not os.path.isdir(db_path):
        logger.error(L("{path}에 폴더가 존재하지 않습니다.", path=db_path))

    os.makedirs(db_temp_path, exist_ok=True)

    observer = Observer()
    observer.schedule(UST_LAB_FileWatcher(db_path, args["table"], db_temp_path, args["use_g2pk4utau"]), db_path, recursive=True)
    observer.start()
    logger.info(L("DB 감시를 시작했습니다."))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    if os.path.isdir(db_temp_path):
        shutil.rmtree(db_temp_path, ignore_errors=True)


if __name__ == "__main__":
    main()
