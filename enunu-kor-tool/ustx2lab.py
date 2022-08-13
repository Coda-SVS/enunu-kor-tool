import os
from glob import glob
from typing import List, Union

import utaupy
from tqdm import tqdm

import g2pk4utau
from utaupyk._ustx2ust import Ustx2Ust_Converter

USE_G2PK4UTAU = True


def convert(input_filepath: str, d_table: dict, g2p_converter: Union[g2pk4utau.g2pk4utau, None] = None):
    assert os.path.isfile(input_filepath)

    ust = utaupy.ust.load(input_filepath, encoding="utf-8")

    length100ns_converter = lambda nt: round(float(25000000 * (int(nt.length) / 20) / int(nt.tempo)))

    # 한 소절 시간 계산 (sil 음소 자동 추가 시도)
    # song_bar_calculator = lambda bpm, beat_numerator, beat_denominator: round(60 / ust * beat_numerator * 4 / beat_denominator * 1000 * 1000 * 10)

    global_length = 0

    phonemes = []
    for idx in range(notes_len := len(ust.notes)):
        note = ust.notes[idx]

        if g2p_converter != None and g2pk4utau.isHangul(note.lyric):
            if idx == 0:
                note_block = ("", note, ust.notes[idx + 1])
            elif idx == notes_len - 1:
                note_block = (ust.notes[idx - 1], note, "")
            else:
                note_block = (ust.notes[idx - 1], note, ust.notes[idx + 1])

            orginal_lyrics = []
            for idx in range(3):
                if isinstance(note_block[idx], utaupy.ust.Note):
                    if idx != 2 or g2pk4utau.isHangul(note_block[idx].lyric):
                        orginal_lyrics.append(note_block[idx].lyric)

            kor_phn_result = g2p_converter("".join(orginal_lyrics))
            kor_phn_token = kor_phn_result[2]

            phns: List[str] = kor_phn_token[1].split(" ")

            phn_time_length = length100ns_converter(note) / len(phns)

            for phn in phns:
                phonemes.append((round(global_length), phn))
                global_length += phn_time_length
        else:
            orginal_lyrics = note.lyric

            phn_time_length = length100ns_converter(note) / len(orginal_lyrics)

            for lyric in orginal_lyrics:
                phonemes.append((round(global_length), *d_table.get(lyric, lyric)))
                global_length += phn_time_length

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


def ustx2lab(table_filepath: str, input_filepath: str, output_dirpath: str):
    input_filepath, output_dirpath = os.path.realpath(input_filepath), os.path.realpath(output_dirpath)

    if (filepath_without_ext := os.path.splitext(input_filepath))[1] == ".ustx":
        converter = Ustx2Ust_Converter(input_filepath, encoding="utf-8")
        input_filepath = (filepath_without_ext := filepath_without_ext[0]) + ".ust"
        converter.save_ust(input_filepath)

    d_table = utaupy.table.load(table_filepath, encoding="utf-8")
    g2p_converter = g2pk4utau.g2pk4utau() if USE_G2PK4UTAU else None

    lab = convert(input_filepath, d_table, g2p_converter)

    for idx, line in enumerate(lab):
        start, end, phn = line
        lab[idx] = f"{start} {end} {phn}"

    os.makedirs(output_dirpath, exist_ok=True)

    with open(os.path.join(output_dirpath, os.path.splitext(os.path.basename(input_filepath))[0] + ".lab"), "w", encoding="utf-8") as f:
        f.write("\n".join(lab))


def main():
    import argparse

    global USE_G2PK4UTAU

    parser = argparse.ArgumentParser(description="UTAU 프로젝트 파일에서 라벨을 추론합니다.")

    parser.add_argument("-d", dest="table", required=True, help="table 파일 경로")
    parser.add_argument("-i", dest="input", required=True, help="단일 Ust 또는 Ustx 파일, 또는 해당 파일이 모여있는 디렉토리 경로")
    parser.add_argument("-o", dest="output", required=True, help="출력 디렉토리 경로")
    parser.add_argument("--no-g2p", dest="notuse_g2pk4utau", action="store_true", help="g2pk4utau를 사용하지 않습니다.")

    args = vars(parser.parse_args())

    USE_G2PK4UTAU = not args["notuse_g2pk4utau"]

    input_files = []
    input_files.extend(glob(os.path.join(args["input"], "*.ust")))
    input_files.extend(glob(os.path.join(args["input"], "*.ustx")))

    for input_filepath in tqdm(input_files, desc="Processing..."):
        ustx2lab(table_filepath=args["table"], input_filepath=input_filepath, output_dirpath=args["output"])

    print("done.")
