import os
from glob import glob
from typing import List
from tqdm import tqdm
from pydub import AudioSegment, effects

from enunu_kor_tool import log, utils


def audio_norm(input_filepath: str, output_filepath: str):
    """오디오 파일에 노멀라이징 효과를 적용합니다.

    Args:
        input_filepath (str): 입력 파일의 경로
        output_filepath (str): 효과가 적용된 오디오 파일의 출력 경로
    """

    ext = os.path.splitext(input_filepath)[1][1:]

    assert ext == "wav", "지원하지 않는 포멧입니다."

    rawsound = AudioSegment.from_file(input_filepath, format=ext)
    normalizedsound = effects.normalize(rawsound)
    normalizedsound.export(output_filepath, format="wav")


def cli_ui_main():
    import cli_ui

    print("> 설명: 음원 파일에 노멀라이징 효과를 적용합니다.")
    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["input"] = cli_ui.ask_string("DB 폴더 경로를 입력하세요.")
    args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력하세요.")

    main(args)


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="음원 파일에 노멀라이징 효과를 적용합니다.")

        parser.add_argument("-i", dest="input", required=True, help="DB 폴더 경로")
        parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")

        args = vars(parser.parse_args())

    logger = log.get_logger(main)

    input_dir = args["input"]
    output_dir = args["output"]

    filepaths = utils.get_files(input_dir, ["wav"])

    os.makedirs(output_dir, exist_ok=True)

    for filepath in tqdm(filepaths, desc="노멀라이징 작업 중..."):
        filename = os.path.splitext(os.path.basename(filepath))[0]
        out_filepath = os.path.join(output_dir, filename) + ".wav"
        audio_norm(filepath, out_filepath)

        logger.info(f"[{filename}] 노멀라이징 처리 완료.")


if __name__ == "__main__":
    main()
