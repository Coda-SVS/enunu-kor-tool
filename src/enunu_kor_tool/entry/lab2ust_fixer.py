import os
import tempfile
from glob import glob
from typing import List

import utaupy
from tqdm import tqdm

from enunu_kor_tool import g2pk4utau, log
from enunu_kor_tool.entry.ustx2lab import ust_notes2phn
from enunu_kor_tool.utaupyk._ustx2ust import Ustx2Ust_Converter

length2ms_converter = lambda length: length / 10000

PAU_LIST = ["pau", "sil"]


def lab2ust_fixer(table_filepath: str, ust_filepath: str, lab_filepath: str, output_dirpath: str, vowel_list: List[str], use_g2pk4utau: bool = False):
    global PAU_LIST

    logger = log.get_logger(lab2ust_fixer)

    ust_filepath, output_dirpath = os.path.realpath(ust_filepath), os.path.realpath(output_dirpath)

    if (filepath_without_ext := os.path.splitext(ust_filepath))[1] == ".ustx":
        converter = Ustx2Ust_Converter(ust_filepath, encoding="utf-8")
        ust_filepath = os.path.join(tempfile.gettempdir(), os.path.basename(filepath_without_ext[0]) + ".ust")
        converter.save_ust(ust_filepath)

    d_table = utaupy.table.load(table_filepath, encoding="utf-8")

    lab = []
    with open(lab_filepath, "r", encoding="utf-8") as f:
        for line in f.readlines():
            start, end, *phn = line.split(" ")
            start = int(start)
            end = int(end)
            phn = "".join(phn).strip()
            lab.append((start, end, phn))

    # pau, sil 통합
    temp_lab = []
    start_pau = None
    for line in lab:
        if line[2] in PAU_LIST:
            if start_pau == None:
                start_pau = line[0]
        else:
            if start_pau != None:
                temp_lab.append((start_pau, line[0], "pau"))
                start_pau = None

            temp_lab.append(line)

    if start_pau != None:
        temp_lab.append((start_pau, lab[-1][1], "pau"))

    lab = temp_lab

    g2p_converter = None
    if use_g2pk4utau:
        g2p_converter = g2pk4utau.g2pk4utau.get_instance()

    ust = utaupy.ust.load(ust_filepath, encoding="utf-8")

    _, lyric_phoneme_pairs = ust_notes2phn(ust, d_table, g2p_converter, os.path.basename(ust_filepath))

    lab_idx = 0
    curr_pos = 0
    for idx, p in enumerate(lyric_phoneme_pairs):
        for phn in p[1]:
            assert (
                phn == lab[lab_idx][2]
            ), f"ust 파일의 음소와 lab 파일의 음소가 일치하지 않습니다. [{p[0]}][{round(curr_pos / 1000 // 60)} min {round(curr_pos / 1000 % 60)} sec] [{phn} != {lab[lab_idx][2]}][{lab_idx + 1}]"
            lab_idx += 1
        curr_pos += ust.notes[idx].length_ms

    note_start_lab_idx = 0
    start = 0
    end = 0

    for idx, ((lyric, phns), note) in enumerate(tqdm(zip(lyric_phoneme_pairs, ust.notes), leave=False)):
        assert lyric == note.lyric, "가사가 일치하지 않습니다."

        lab_idx = note_start_lab_idx

        start = lab[lab_idx][0]  # 현재 노트에 해당하는 음소들의 시작
        for p in phns:
            if p in vowel_list:
                start = lab[lab_idx][0]
                break

            lab_idx += 1

        lab_idx = note_start_lab_idx
        end = lab[note_start_lab_idx + len(phns) - 1][1]  # 현재 노트에 해당하는 음소들의 끝

        if idx < len(ust.notes) - 1:
            next_lyric, next_phns = lyric_phoneme_pairs[idx + 1]
            if len(next_phns) == 1:  # 다음 노트의 음소가 하나 뿐일 경우
                pass
            elif next_phns[0] not in vowel_list:
                lab_idx = note_start_lab_idx + len(phns)  # 다음 노트 음소들의 시작 Index
                end = lab[lab_idx][1]
                for p in next_phns:
                    if p in vowel_list:
                        break
                    end = lab[lab_idx][1]
                    lab_idx += 1

        before_note_length = note.length_ms
        note.length_ms = length2ms_converter(end - start)

        logger.info(f"* [{str(idx).rjust(4)}] [{note.lyric}] : [{before_note_length}] -> [{note.length_ms}]")

        note_start_lab_idx += len(phns)

    os.makedirs(output_dirpath, exist_ok=True)

    ust.write(os.path.join(output_dirpath, os.path.splitext(os.path.basename(ust_filepath))[0] + ".ust"), encoding="utf-8")


def cli_ui_main():
    import cli_ui

    print("> 설명: 해당 모듈은 LAB 파일로 UST 파일의 타이밍을 보정합니다.")
    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["table"] = cli_ui.ask_string("table 파일 경로를 입력하세요.")
    args["vowel_list"] = cli_ui.ask_string("모음 리스트를 입력하세요. (,로 구분)")
    args["input"] = cli_ui.ask_string("DB 폴더 경로를 입력하세요.")
    args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력하세요.")
    args["notuse_g2pk4utau"] = cli_ui.ask_yes_no("g2pk4utau 미사용", default=False)

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="LAB 파일로 UST 파일의 타이밍을 보정합니다.")

        parser.add_argument("-d", dest="table", required=True, help="table 파일 경로")
        parser.add_argument("-p", dest="vowel_list", required=True, help="모음 리스트 (,로 구분)")  # kor: a,eo,o,u,i,eu,e,y,w
        parser.add_argument("-i", dest="input", required=True, help="DB 폴더 경로")
        parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")
        parser.add_argument("--no-g2p", dest="notuse_g2pk4utau", action="store_false", help="g2pk4utau를 사용하지 않습니다.")

        args = vars(parser.parse_args())

    use_g2pk4utau = args["notuse_g2pk4utau"]

    ust_ustx_files = []
    ust_ustx_files.extend(glob(os.path.join(args["input"], "*.ustx")))
    ust_ustx_files.extend(glob(os.path.join(args["input"], "*.ust")))
    lab_files = glob(os.path.join(args["input"], "*.lab"))

    vowel_list: List[str] = [p.strip() for p in args["vowel_list"].split(",")]

    # Duplicate input file filter
    templist = []
    filename_filter = []
    for file_fullname in ust_ustx_files:
        if not (filename := os.path.splitext(os.path.basename(file_fullname))[0]).endswith("-autosave") and filename not in filename_filter:
            filename_filter.append(filename)
            templist.append(file_fullname)
    ust_ustx_files = templist

    lab_files_dict = {}
    for filepath in lab_files:
        lab_files_dict[os.path.splitext(os.path.basename(filepath))[0]] = filepath

    for ust_ustx_filepath in (input_filepath_tqdm := tqdm(ust_ustx_files)):
        filename = os.path.splitext(os.path.basename(ust_ustx_filepath))[0]
        if filename not in lab_files_dict:
            print(f"파일 이름이 일치하는 lab 파일을 찾을 수 없습니다. [filename={filename}]")
            continue

        input_filepath_tqdm.set_description(f"Processing... [{os.path.basename(ust_ustx_filepath)}]")
        try:
            lab2ust_fixer(
                table_filepath=args["table"],
                ust_filepath=ust_ustx_filepath,
                lab_filepath=lab_files_dict[filename],
                output_dirpath=args["output"],
                vowel_list=vowel_list,
                use_g2pk4utau=use_g2pk4utau,
            )
        except AssertionError as ex:
            print(f"AssertionError: [{os.path.split(os.path.basename(ust_ustx_filepath))[0]}] {ex=}")

    print("done.")


if __name__ == "__main__":
    main()
