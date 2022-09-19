import os
from pprint import pprint
from tqdm import tqdm
from glob import glob


def cli_ui_main():
    import cli_ui

    print("> 설명: 해당 모듈은 라벨 파일의 음소만 남기고, 시간은 지웁니다.")
    print("* TIP: 파일이나 폴더의 경로를 입력할 때, 드래그 & 드롭으로 쉽게 입력할 수 있습니다.")

    args = {}

    args["input"] = cli_ui.ask_string("단일 lab 파일, 또는 해당 파일이 모여있는 폴더 경로를 입력해주세요.")
    args["output"] = cli_ui.ask_string("출력 폴더 경로를 입력해주세요.")

    main(args)


def lab2ntlab(path: str, output_path: str, suffix: str = ""):
    os.makedirs(output_path, exist_ok=True)

    phn = []
    with open(path, "r", encoding="utf-8") as f:
        phn = [" ".join(line.strip("\n ").split(" ")[2:]) for line in f.readlines()]

    filename, ext = os.path.splitext(os.path.basename(path))
    filename = f"{filename}_no-time{suffix}{ext}"

    pprint(phn)

    with open(os.path.join(output_path, filename), "w", encoding="utf-8") as f:
        f.write("\n".join(phn) + "\n")


def main(args=None):
    if not isinstance(args, dict):
        import argparse

        parser = argparse.ArgumentParser(description="라벨 파일의 음소만 남기고, 시간은 지웁니다.")

        parser.add_argument("-i", dest="input", required=True, help="단일 lab 파일, 또는 해당 파일이 모여있는 폴더 경로")
        parser.add_argument("-o", dest="output", required=True, help="출력 폴더 경로")

        args = vars(parser.parse_args())

    if os.path.isfile(args["input"]):
        input_files = [args["input"]]
    else:
        input_files = glob(os.path.join(args["input"], "*.lab"))

    templist = []
    for file_fullname in input_files:
        if not os.path.splitext(os.path.basename(file_fullname))[0].endswith("_no-time"):
            templist.append(file_fullname)
    input_files = templist

    for input_filepath in tqdm(input_files, desc="Processing..."):
        lab2ntlab(input_filepath, args["output"])


if __name__ == "__main__":
    main()
