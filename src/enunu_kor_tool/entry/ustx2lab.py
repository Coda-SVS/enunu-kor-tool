import os
from glob import glob
from typing import Union

import utaupy
from tqdm import tqdm

from enunu_kor_tool import g2pk4utau
from enunu_kor_tool.utaupyk._ustx2ust import Ustx2Ust_Converter
from enunu_kor_tool.utaupyk._ust2hts import ustnote2htsnote


def ust_notes2phn(ust: utaupy.ust.Ust, d_table: dict, g2p_converter: Union[g2pk4utau.g2pk4utau, None] = None, filename: str = ""):
    length100ns_converter = lambda nt: round(float(25000000 * (int(nt.length) / 20) / int(nt.tempo)))

    # 한 소절 시간 계산 (sil 음소 자동 추가 시도)
    # song_bar_calculator = lambda bpm, beat_numerator, beat_denominator: round(60 / ust * beat_numerator * 4 / beat_denominator * 1000 * 1000 * 10)

    global_length = 0

    phonemes = []
    lyric_phoneme_pairs = []
    for idx in tqdm(range(notes_len := len(ust.notes)), leave=False):
        note = ust.notes[idx]
        prev_note = ust.notes[idx - 1] if idx != 0 else ""
        next_note = ust.notes[idx + 1] if idx + 1 < notes_len else ""
        ust_note_block = [prev_note, note, next_note]

        if note.lyric != note.lyric.strip():
            tqdm.write(f'Warning: "{note.lyric}" 불필요한 문자가 포함됨.' + "" if filename == "" else f" from [{filename}]")

        hts_note = ustnote2htsnote(ust_note_block, d_table, g2p_converter)
        # hts_note: utaupy.hts.Note
        phns = [phn.identity for phn in hts_note.phonemes]

        phn_time_length = length100ns_converter(note) / len(phns)

        for phn in phns:
            phonemes.append((round(global_length), phn))
            global_length += phn_time_length

        lyric_phoneme_pairs.append((note.lyric, phns))

    return phonemes, lyric_phoneme_pairs


def convert(filename: str, ust: utaupy.ust.Ust, d_table: dict, g2p_converter: Union[g2pk4utau.g2pk4utau, None] = None):
    phonemes, _ = ust_notes2phn(ust, d_table, g2p_converter, filename)

    result = []
    phonemes_len = len(phonemes)
    sum_length = 0

    for idx, (start, phn) in enumerate(phonemes):
        if phonemes_len > idx + 1:
            end = phonemes[idx + 1][0]
            result.append((start, end, phn))
            sum_length += end - start
        else:
            result.append((start, start + round(sum_length / phonemes_len - 1), phn))

    return result


def ustx2lab(table_filepath: str, input_filepath: str, output_dirpath: str, use_g2pk4utau: bool = False, use_timeline: bool = True):
    input_filepath, output_dirpath = os.path.realpath(input_filepath), os.path.realpath(output_dirpath)

    if (filepath_without_ext := os.path.splitext(input_filepath))[1] == ".ustx":
        converter = Ustx2Ust_Converter(input_filepath, encoding="utf-8")
        input_filepath = (filepath_without_ext := filepath_without_ext[0]) + ".ust"
        converter.save_ust(input_filepath)

    d_table = utaupy.table.load(table_filepath, encoding="utf-8")

    g2p_converter = None
    if use_g2pk4utau:
        g2p_converter = g2pk4utau.g2pk4utau.get_instance()

    ust = utaupy.ust.load(input_filepath)

    lab = convert(os.path.basename(input_filepath), ust, d_table, g2p_converter)

    for idx, line in enumerate(lab):
        start, end, phn = line
        if use_timeline:
            lab[idx] = f"{start} {end} {phn}"
        else:
            lab[idx] = phn

    os.makedirs(output_dirpath, exist_ok=True)

    with open(os.path.join(output_dirpath, os.path.splitext(os.path.basename(input_filepath))[0] + ".lab"), "w", encoding="utf-8") as f:
        f.write("\n".join(lab) + "\n")


def cli_ui_main():
    import cli_ui

    print("> 설명: 해당 모듈은 UTAU 프로젝트 파일에서 라벨을 자동 생성합니다.")
    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["table"] = cli_ui.ask_string("table 파일 경로를 입력하세요.")
    args["input"] = cli_ui.ask_string("단일 Ust 또는 Ustx 파일, 또는 해당 파일이 모여있는 폴더 경로를 입력하세요.")
    args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력하세요.")
    args["notuse_timeline"] = cli_ui.ask_yes_no("lab 파일의 음소만 출력", default=False)
    args["notuse_g2pk4utau"] = cli_ui.ask_yes_no("g2pk4utau 미사용", default=False)

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="UTAU 프로젝트 파일에서 라벨을 자동 생성합니다.")

        parser.add_argument("-d", dest="table", required=True, help="table 파일 경로")
        parser.add_argument("-i", dest="input", required=True, help="단일 Ust 또는 Ustx 파일, 또는 해당 파일이 모여있는 폴더 경로")
        parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")
        parser.add_argument("--no-time", dest="notuse_timeline", action="store_false", help="시간을 출력하지 않습니다.")
        parser.add_argument("--no-g2p", dest="notuse_g2pk4utau", action="store_false", help="g2pk4utau를 사용하지 않습니다.")

        args = vars(parser.parse_args())

    use_g2pk4utau = args["notuse_g2pk4utau"]
    use_timeline = args["notuse_timeline"]

    input_files = []
    if os.path.isfile(args["input"]):
        input_files.append(args["input"])
    else:
        input_files.extend(glob(os.path.join(args["input"], "*.ustx")))
        input_files.extend(glob(os.path.join(args["input"], "*.ust")))

    # Duplicate input file filter
    templist = []
    filename_filter = []
    for file_fullname in input_files:
        if not (filename := os.path.splitext(os.path.basename(file_fullname))[0]).endswith("-autosave") and filename not in filename_filter:
            filename_filter.append(filename)
            templist.append(file_fullname)
    input_files = templist

    for input_filepath in (input_filepath_tqdm := tqdm(input_files, leave=False)):
        input_filepath_tqdm.set_description(f"Processing... [{os.path.basename(input_filepath)}]")
        ustx2lab(table_filepath=args["table"], input_filepath=input_filepath, output_dirpath=args["output"], use_g2pk4utau=use_g2pk4utau, use_timeline=use_timeline)

    print("done.")


if __name__ == "__main__":
    main()
