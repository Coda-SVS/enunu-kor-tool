import os
from glob import glob

import numpy as np
import soundfile as sf
from tqdm import tqdm

from enunu_kor_tool import log


def get_filepath_from_inputpath(input_path: str, path: str, abspath: bool = True):
    if abspath:
        path = path.replace(input_path, "")
        while path.startswith((os.path.sep, ".")):
            path = path[1:]
    else:
        path = os.path.basename(path)

    return os.path.splitext(path)[0]


def cut2sil(wav_filepath: str, lab_filepath: str, output_dirpath: str, sil_notations: str, max_sil_dur_ms: int = 5000):
    # logger = log.get_logger(cut2sil)

    # 10000000 == 1초

    lab = []
    with open(lab_filepath, "r", encoding="utf-8") as f:
        for line in f.readlines():
            start, end, *phn = line.split(" ")
            start = int(start)
            end = int(end)
            phn = "".join(phn).strip()
            lab.append((start, end, phn))

    max_sil_dur = max_sil_dur_ms / 1000

    y, sr = sf.read(wav_filepath)

    before_pos = 0
    lab = [[end, phn] for _, end, phn in lab]
    for idx in range(len(lab)):
        changed = False
        curr_end, curr_phn = lab[idx]

        if curr_phn in sil_notations and (curr_end - before_pos) // 10000000 > max_sil_dur:
            wav_start = before_pos / 10000000
            wav_end = curr_end / 10000000
            changed = True

            y_front = y[: round(sr * (wav_start + max_sil_dur))]
            y_back = y[round(sr * wav_end) :]
            y = np.concatenate((y_front, y_back), axis=0)

        if changed and idx + 1 < len(lab):
            before_pos += round(max_sil_dur * 10000000)
            lab[idx][0] = before_pos
            for l in lab[idx + 1 :]:
                l[0] -= curr_end - before_pos
        else:
            before_pos = curr_end

    end_offset = 50000  # lab은 무조건 wav보다 짧아야하므로 offset 추가
    y = y[: round(sr * ((lab[-1][0] + end_offset) / 10000000))]

    result_lab = []
    before_end = 0
    for end, phn in lab:
        result_lab.append((str(before_end), str(end), phn))
        before_end = end

    os.makedirs(output_dirpath, exist_ok=True)

    sf.write(os.path.join(output_dirpath, os.path.basename(wav_filepath)), y, sr)

    with open(os.path.join(output_dirpath, os.path.basename(lab_filepath)), "w", encoding="utf-8") as f:
        temp_lines = []
        for line in result_lab:
            temp_lines.append(" ".join(line))
        f.write("\n".join(temp_lines))


def cli_ui_main():
    import cli_ui

    print("> 설명: 해당 모듈은 데이터의 너무 긴 무음 부분은 자릅니다.")
    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["input"] = cli_ui.ask_string("DB 폴더 경로를 입력하세요.")
    args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력하세요.")
    args["sil_char"] = cli_ui.ask_string("무음 음소를 입력하세요. [기본값: sil]", default="sil")
    args["max_sil_dur_ms"] = int(cli_ui.ask_string("최대 무음 길이를 입력하세요. [기본값: 5000 ms]", default="5000"))

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="데이터의 너무 긴 무음 부분은 자릅니다.")

        parser.add_argument("-p", dest="sil_char", default="sil", help="무음 음소")
        parser.add_argument("-i", dest="input", required=True, help="DB 폴더 경로")
        parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")
        parser.add_argument("--max_sil_dur", dest="max_sil_dur_ms", default=5000, help="최대 무음 길이 (ms)")

        args = vars(parser.parse_args())

    logger = log.get_logger(main)

    sil_notation: str = args["sil_char"].strip()
    max_sil_dur_ms = int(args["max_sil_dur_ms"])

    wav_files = {}
    lab_files = {}

    wav_input_filepaths = glob(os.path.join(args["input"], "*.wav"))
    # wav_input_filepaths.extend(glob(os.path.join(args["input"], "**", "*.wav"), recursive=True))
    for wav_filepath in wav_input_filepaths:
        wav_files[get_filepath_from_inputpath(args["input"], wav_filepath)] = wav_filepath

    lab_input_filepaths = glob(os.path.join(args["input"], "*.lab"))
    # lab_input_filepaths.extend(glob(os.path.join(args["input"], "**", "*.lab"), recursive=True))
    for lab_filepath in lab_input_filepaths:
        lab_files[get_filepath_from_inputpath(args["input"], lab_filepath)] = lab_filepath

    assert len(wav_input_filepaths) > 0 or len(lab_input_filepaths) > 0, "입력된 파일이 없습니다!"

    # input file filter
    input_files = []
    filename_filter = []
    for file_fullname in wav_input_filepaths:
        filename = get_filepath_from_inputpath(args["input"], file_fullname)

        if filename not in filename_filter:
            filename_filter.append(filename)

            if filename in wav_files and filename in lab_files:
                input_files.append((wav_files[filename], lab_files[filename]))
            else:
                logger.warn(f"완전하지 않은 데이터가 있습니다. (lab 파일 누락) [{filename}]")

    for wav_fp, lab_fp in (input_filepath_tqdm := tqdm(input_files)):
        input_filepath_tqdm.set_description(f"Processing... [{wav_fp}][{lab_fp}]")
        cut2sil(wav_fp, lab_fp, args["output"], sil_notation, max_sil_dur_ms)

    print("done.")


if __name__ == "__main__":
    main()


# def cli_ui_main():
#     import cli_ui

#     print("> 설명: 해당 모듈은 데이터의 너무 긴 무음 부분은 자릅니다.")
#     print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

#     args = {}

#     args["input"] = cli_ui.ask_string("DB 폴더 경로를 입력하세요.")
#     args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력하세요.")
#     args["sil_chars"] = cli_ui.ask_string("무음 표기를 입력하세요. (콤마(,)로 구분)[기본값: sil]", default="R,sil")
#     args["max_sil_dur_ms"] = int(cli_ui.ask_string("최대 무음 길이를 입력하세요. [기본값: 5000 ms]", default="5000"))

#     main(args)


# def main(args=None):
#     if not isinstance(args, dict):
#         import argparse

#         parser = argparse.ArgumentParser(description="데이터의 너무 긴 무음 부분은 자릅니다.")

#         parser.add_argument("-p", dest="sil_chars", default="R,sil", help="무음 표기 (콤마(,)로 구분)")
#         parser.add_argument("-i", dest="input", required=True, help="DB 폴더 경로")
#         parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")
#         parser.add_argument("--max_sil_dur", dest="max_sil_dur_ms", default=5000, help="최대 무음 길이 (ms)")

#         args = vars(parser.parse_args())

#     logger = log.get_logger(main)

#     sil_notations: List[str] = [t.strip() for t in args["sil_chars"].split(",")]
#     max_sil_dur_ms = int(args["max_sil_dur_ms"])

#     ust_ustx_files = []
#     wav_files = {}
#     lab_files = {}

#     ust_ustx_files.extend(glob(os.path.join(args["input"], "*.ustx"), recursive=True))
#     ust_ustx_files.extend(glob(os.path.join(args["input"], "**", "*.ustx"), recursive=True))
#     ust_ustx_files.extend(glob(os.path.join(args["input"], "*.ust"), recursive=True))
#     ust_ustx_files.extend(glob(os.path.join(args["input"], "**", "*.ust"), recursive=True))

#     wav_input_filepaths = glob(os.path.join(args["input"], "*.wav"), recursive=True)
#     wav_input_filepaths.extend(glob(os.path.join(args["input"], "**", "*.wav"), recursive=True))
#     for wav_filepath in wav_input_filepaths:
#         wav_files[get_filepath_from_inputpath(args["input"], wav_filepath)] = wav_filepath

#     lab_input_filepaths = glob(os.path.join(args["input"], "*.lab"), recursive=True)
#     lab_input_filepaths.extend(glob(os.path.join(args["input"], "**", "*.lab"), recursive=True))
#     for lab_filepath in lab_input_filepaths:
#         lab_files[get_filepath_from_inputpath(args["input"], lab_filepath)] = lab_filepath

#     assert len(ust_ustx_files) > 0 and len(wav_input_filepaths) > 0 or len(lab_input_filepaths) > 0, "입력된 파일이 없습니다!"

#     # input file filter
#     input_files = []
#     filename_filter = []
#     for file_fullname in ust_ustx_files:
#         if not (filename := get_filepath_from_inputpath(args["input"], file_fullname)).endswith("-autosave") and filename not in filename_filter:
#             filename_filter.append(filename)

#             if filename in wav_files and filename in lab_files:
#                 input_files.append((wav_files[filename], file_fullname, lab_files[filename]))
#             else:
#                 logger.warn(f"완전하지 않은 데이터가 있습니다. (wav or lab 파일 누락) [{filename}]")

#     for wav_fp, ust_fp, lab_fp in (input_filepath_tqdm := tqdm(input_files)):
#         input_filepath_tqdm.set_description(f"Processing... [{wav_fp}][{ust_fp}][{lab_fp}]")
#         cut2sil(wav_fp, ust_fp, lab_fp, args["output"], sil_notations, max_sil_dur_ms)

#     print("done.")
